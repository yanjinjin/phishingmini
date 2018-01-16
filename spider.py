#!/usr/bin/env python
from Queue import Queue, Empty
import urllib2
from urllib2 import *
import requests
import threading
from threading import Thread
import re
import hashlib
import urlparse
import os
import traceback
import thread
from os import path
from datetime import datetime
from time import ctime,sleep
import pickle
import StringIO
import gzip
import signal
import random
import gc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# for trace memory
random.seed(0)

#so i can search keyword debug to remove it
def debug(msg):
    print msg
    
SAFELOCKER = threading.Lock()
def safe_print(msg):
    SAFELOCKER.acquire()
    print "[%s] %s" % (datetime.now(), msg)
    SAFELOCKER.release()
    
DATEFMT = "%Y-%m-%d %H:%M:%S"


class Job:
    '''
    job contains all the information downloader need to know to download
    '''
    def __init__(self, url, referer = None, retry_times = 0):
        self.url = url
        self.referer = referer
        self.retry_times = retry_times

    def get_retry_times(self):
        return self.retry_times

    def get_link(self):
        return self.url

    def get_referer(self):
        return self.referer

    def get_joined_link(self):
        if self.referer == None:
            return self.url
        else:
            return urlparse.urljoin(self.referer, self.url)
    
    def get_id(self):
        return hashlib.md5(re.sub(r"#.*$", "", self.get_joined_link())).hexdigest() 

    def __str__(self):
        return self.url

class Utility:
    @staticmethod
    def get_local_path(refer, url, is_relative = True):
        if Utility.is_js_label(url):
            return url
        if refer == None:
            refer = ""
        url = urlparse.urljoin(refer, url)
        ret = urlparse.urlparse(url)  
        
        path = ret.path
        if ret.path in ['/', '']:
            path = '/index.html'
        elif ret.path[-1] == '/':
            path = ret.path + 'index.html'
        query_str = ret.query.replace('?', '-').replace('=', '-').replace('&', '-').replace("://", '-').replace('.', '-')

        if len(url) > 200:
            query_str = hashlib.md5(query_str).hexdigest() 

        path_comps = path.split('/')
        last_piece = path_comps[-1]

        if '.' in last_piece:
            sps = last_piece.rsplit('.', 1)

            if len(sps) == 2:
                path_comps[-1] = sps[0] + query_str + '.' + sps[1]

         
        retval = "%s%s" % (ret.netloc.replace('.', '-'), '/'.join(path_comps))

        if not is_relative:
            return retval
        else:
            ref_abs = Utility.get_local_path("", refer, False)
            return Utility.get_relative_path(ref_abs, retval)

    @staticmethod
    def get_relative_path(a, b):
        ''' 
        b relative to a
        example:
        /root/x/1.html; /root/y/2.html
        the result is ../../y/2.html
        '''
        a_parts = a.split("/")
        b_parts = b.split("/")

        for i in xrange(len(a_parts)):
            if i >= len(b_parts):
                break
            if a_parts[i] != b_parts[i]:
                break
        
        return "../" * (len(a_parts) - i - 1) + "/".join(b_parts[i:])


    @staticmethod
    def is_js_label(url):
        '''
        javascript label may exist in src attribute, test for that.
        '''
        if url.strip().startswith('javascript:'):
            return True
        return False

class Parser:
    '''
    parse html, css documents to find urls in them
    '''

    #href, src, url, import from which an url appears
    href_regex = re.compile(r"(href\s*=\s*([\"'])([^\"']+)\2)", re.IGNORECASE)
    src_regex = re.compile(r"(src\s*=\s*([\"'])([^\"']+)\2)", re.IGNORECASE)
    back_images_regex = re.compile(r"(url\s*\(\s*([\"']*)([^\"'()]+)\2)\)", re.IGNORECASE)
    css_import_regex = re.compile(r"(@import\s*\(\s*([\"']*)([^\"'()]+)\2)\)", re.IGNORECASE)

    def parse(self, content, url, store_path, c_charset):
        self.store_path = store_path.rstrip('/')
        self.content = content
        self.url = url

        links = []
        for rx, link_pos in [(Parser.href_regex, 2), (Parser.src_regex, 2), (Parser.back_images_regex, 2), (Parser.css_import_regex, 2)]:
            links += self.replace_url_in_content(rx, link_pos, c_charset)

        return links

    def replace_url_in_content(self, regex, link_pos, c_charset):
        '''
        file will be store in local disk, so we need to replace the original urls in them with the one using file: schemal
        '''
        founded = regex.findall(self.content)

        links = []
        for fd in founded:
            full = fd[0]
            link = fd[link_pos]

            ps_ret = urlparse.urlparse(link)
            t = urlparse.urlparse(urlparse.urljoin(self.url, link))

            if t.scheme == 'http' or t.scheme == 'https':
                new_full = full.replace(link, "%s#%s" % (Utility.get_local_path(self.url, link), ps_ret.fragment))
                self.content = self.content.replace(full, new_full) 
                #if c_charset:
                #    link.encode(c_charset)
                links.append(link)

        return links

    def get_changed_content(self):
        return self.content

class RememberFailedError(Exception):
    pass

#Store will make sure that there won't be two thread write to one memery place
class Memory:
    '''
    provide an interface the remember the downloaded files. also we can query if the url has been downloaded from this class
    '''
    def __init__(self, memery_place):
        self.memery_place = path.join(memery_place, ".gwd", "mem")
        if not path.isdir(self.memery_place):
            os.makedirs(self.memery_place)
    def remember(self, job, links):
        '''
        remember the downloaded urls
        '''
        f = None
        try:
            f = open(self.get_memery_place(job), 'w')
            for link in links:
                new_job = Job(link, job.get_joined_link())
                f.write(("%s\n" % new_job.get_joined_link()))
        except IOError, e:
            raise RememberFailedError(e)
        finally:
            if f != None:
                f.close()

    def remembered(self, job):
        '''
        query if the url(job) has been downloaded(done)
        '''
        f = None
        try:
            mem_place = self.get_memery_place(job)

            if not os.path.isfile(mem_place):
                return None
            f = open(mem_place, 'r')
            content = f.read().rstrip("\n")

            if content:
                links = content.split("\n")
            else:
                links = []

            jobs = []
            for link in links:
                jobs.append(Job(link, ""))
            return jobs
        except IOError, e:
            raise RememberFailedError(e)
        finally:
            if f != None:
                f.close()

    def get_memery_place(self, job):
        return path.join(self.memery_place, job.get_id())

class Processer:
    def do_process(self, job, c_t, c_charset, content):
        pass

class SaveFileProcesser(Processer):
    def __init__(self, store):
        self.store = store

    def do_process(self, job, c_t, c_charset, content):
        localpath = Utility.get_local_path(job.get_referer(), job.get_link(), False)
        localpath = os.path.join(self.store.get_store_path(), localpath) 

        dir = os.path.dirname(localpath)
        file_name = os.path.basename(localpath)

        if not os.path.isdir(dir):
            os.makedirs(dir, 0755)

        f = None
        try:
            f = open(localpath, 'w+')
            #if c_charset != None:
            #    f.write(content.encode(c_charset))
            #else:
            #    f.write(content)

            f.write(content)

        except IOError:
            safe_print("can't write to %s" % localpath)
        finally:
            if f != None:
                f.close()

class Downloader:
    '''
    contains the logic to download from an url
    '''
    '''white_lists =  ['text/html', 'text/css', 'text/plain', \
                    'text/xml', 'text/javascript', 'image/png', \
                    'image/gif', 'image/jpeg', 'application/x-javascript', \
                    'application/xml', 'application/javascript', \
                    "application/json"]
    '''
    white_lists =  ['text/html','text/xml','text/csv']

    """download from an url, it will download all files related with this url"""
    def __init__(self, store, mem_inst):
        self.store = store
        self.parser = Parser()
        self.mem_inst = mem_inst
        self.exit = False
        self.processer = SaveFileProcesser(self.store)
        #self.processer = ExtractBookProcesser(self.store.get_store_path() + "/__book__")

    def kill(self):
        self.exit = True

    def download(self):
        '''
        download routine
        '''
        while not (self.exit or DHManager.all_is_done):
            try:
                job = self.store.get()
            except Empty, e:
        	time.sleep(1)
	        continue

            #print job
            if Utility.is_js_label(job.get_link()):
                self.store.task_done()
                continue


            mem_jobs = self.mem_inst.remembered(job)
            if mem_jobs != None:
                try:
                    for mem_job in mem_jobs:
                        self.store.put(mem_job)
                    continue
                except RememberFailedError, e:
                    raise e
                finally:
                    self.store.mark_as_done(job)
                    self.store.task_done()

            link = job.get_joined_link()
            try:
                bechmark_start = datetime.now()
                c, c_t, c_charset = self.get_content(job)
                bechmark_end = datetime.now()
                safe_print("[%d]download %s, takes %s" % (self.store.qsize(), link, bechmark_end - bechmark_start))

                if c_t in ['text/html', 'text/css']:
                    links = self.parser.parse(c, link, self.store.get_store_path(), c_charset)
                    c = self.parser.get_changed_content()
                else:
                    links = []

                self.processer.do_process(job, c_t, c_charset, c);

                self.mem_inst.remember(job, links)
                for lk in links:
                    self.store.put(Job(lk, link))
                
                self.store.mark_as_done(job)

            except URLError, e:
                safe_print("can't down load from %s %s" % (link, e))
                
                if job.get_retry_times() < 10:
                    new_job = Job(link, link, job.get_retry_times() + 1) 
                    self.store.put(new_job)
                else:
                    self.mem_inst.remember(job, links)
                    self.store.mark_as_done(job)
                    safe_print("exceed 10 retry times")
                    #os._exit(1)
            except RememberFailedError, e:
                raise e
            except Exception, e:
                if str(e) == "timed out" and job.get_retry_times() < 100:
                    self.store.put(Job(link, link))
                else:
                    safe_print("exceed 100 retry times")
                    #os._exit(1)
                safe_print("error happended %s, url %s" % (e, link))
                traceback.print_exc()
                #continue
            finally:
                self.store.task_done()
		time.sleep(2*random.random()+1)#sleep 1~2 good spider
		safe_print("one task download over")

    def __ungzip(self, content):
        cs = StringIO.StringIO(content)
        gzipper = gzip.GzipFile(fileobj=cs)
        return gzipper.read()
            
    def get_content(self, job):
        '''
        use urllib to download the file
        '''
        url = job.get_joined_link()
        headers = {"Accept":"text/html","Referer":"http://www.sijitao.net/","User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"}

        request = Request(url, None, headers)
	fh = None
	if self.store.proxys!=[] and self.store.proxys!=None:
	    for i in self.store.proxys:
		try:
		    #p = random.choice(range(0, len(self.store.proxys)))
                    dict = {}
                    dict['http'] = i
                    print dict
                    #dict['http']="110.16.80.106:8080"
                    proxy_handler=urllib2.ProxyHandler(dict)
                    opener=urllib2.build_opener(proxy_handler)
                    urllib2.install_opener(opener)
                    fh = urllib2.urlopen(request, timeout = 20)
		    break
	        except:		
		    continue
        else:
	    fh = urllib2.urlopen(request, timeout = 60 * 2)
        content = fh.read()
	#content = requests.get(url,headers = headers,proxies = dict,timeout = 30)
        ct = fh.headers['Content-Type']
        match = re.match(r'(.*);', ct)

        if match != None:
            con_type = match.groups()[0]
        else:
            if 'charset' not in ct:
                con_type = ct.rstrip(';')
            else:   
                con_type = ct

        if ('Content-Encoding' in fh.headers) and (con_type == 'text/html'):
            if fh.headers['Content-Encoding'] == 'gzip':
                content = self.__ungzip(content)

        print ct
        con_charset = None
        if con_type == "text/html" or con_type == "text/css":
            match = re.search(r'charset=([^"]+)', ct)
            if match:
                con_charset = match.groups()[0].lower()
            elif con_type == "text/html":
                match = re.search(r'[\t ]+charset=(["\']?)([^"\']+)\1', content)
                if match:
                    con_charset = match.groups()[1].lower()

            if con_charset == None:
                con_charset = "utf-8"
            #content = content.decode(con_charset)

        if con_type in Downloader.white_lists:
            return (content, con_type, con_charset)
        else:
            safe_print(con_type)
            return ("", con_type, con_charset)

class Filter:
    '''
    tell us what kind of file should be downloaded and what should not be
    '''
    def __init__(self):
        self.ft = set()

    def add_filter(self, *args):
        '''
        add filter rules
        '''
        for filter in args:
            self.ft.add(filter)

    def passed(self):
        '''
        check if passed
        '''
        if len(self.ft) == 0:
            return True
        else:
            return False

class WhiteList(Filter):
    def passed(self, url):
        if  Filter.passed(self):
            return True

        else:
            for filter in self.ft:
                if re.search(filter, url):
                    return True
            return False

class BlackList(Filter):
    def passed(self, url):
        if  Filter.passed(self):
            return True

        else:
            for filter in self.ft:
                if re.search(filter, url):
                    return False
            return True

class StoreError(Exception):
    pass

class Checker:
    MAX_POOL_SIZE = 1024 * 10
    def __init__(self, checker_place):

        self.checker_place = path.join(checker_place, ".gwd", "checker")
        if not path.isdir(self.checker_place):
            os.makedirs(self.checker_place)

        self.mutex = threading.Lock()  
        self.pool = set()
        self.second_pool = set()
        self.cur_file_num = -1
        self.file_base_name = "checker_file_"
    def add(self, v):
        if self.check(v):
            return

        try:
            self.mutex.acquire()

            if len(self.pool) >= Checker.MAX_POOL_SIZE / len(v):
                if len(self.second_pool) != 0:
                    self.__dump_pool(self.second_pool)
                    gc.collect()
            
                self.second_pool = self.pool
                self.pool = set()

            self.pool.add(v)
        finally:
            self.mutex.release()

    def check(self, v):
        try:
            self.mutex.acquire()

            if v in self.pool or v in self.second_pool:
                return True
            if self.cur_file_num == -1:
                return False

            for i in xrange(self.cur_file_num, -1, -1):
                p = self.__load_pool(i)
                if v in p:
                    return True

            return False
        finally:
            self.mutex.release()

    def __load_pool(self, num):
        f = open(self.__get_file_path(num), 'r')
        ret = pickle.load(f)
        f.close()
        return ret

    def __dump_pool(self, p):
        self.cur_file_num += 1

        f = open(self.__get_file_path(self.cur_file_num), 'w')
        pickle.dump(p, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def __get_file_path(self, num):
        return path.join(self.checker_place, "%s%d" % (self.file_base_name, num))

class Store(Queue):
    '''
    a wrapper class to Queue.Queue, so we can control the get and put process
    '''
    def __init__(self, proxys , store_path):
        Queue.__init__(self)
	self.proxys = proxys
        self.store_path = store_path
        self.whitelist = WhiteList()
        self.blacklist = BlackList()

        self.checker = Checker(store_path)

    def put(self, job):
        if self.pass_filters(job):
            Queue.put(self, job)

    def get(self):
        while True:
            '''
            if Queue.empty(self):
                raise StoreEmptyError()
            '''

            job = Queue.get(self, True, 0.01)

            if not self.checker.check(job.get_id()):
                return job
            else:
                self.task_done()

    def mark_as_done(self, job):
        self.checker.add(job.get_id())

    def get_store_path(self):
        return self.store_path

    def add_filter(self, t, *args):
        for arg in args:
            if arg == "{image}":
                t.add_filter("\.(jpg|jpeg|gif|png)([?#]|$)")
            elif arg == "{css}":
                t.add_filter("\.css([?#]|$)")
            elif arg == "{javascript}":
                t.add_filter("\.js([?#]|$)")
            else:
                t.add_filter(arg)

    def add_white_filter(self, *args):
        self.add_filter(self.whitelist, *args);

    def add_black_filter(self, *args):
        self.add_filter(self.blacklist, *args);

    def pass_filters(self, job):
        link = job.get_joined_link()
        if self.blacklist.passed(link):
            if self.whitelist.passed(link):
                return True
            else:
                return False
        else:
            return False

class DH(threading.Thread):
    '''
    download thread
    '''
    def __init__(self, store, mem_inst):
        Thread.__init__(self)
        self.downloader = Downloader(store, mem_inst)
        
    def run(self):
        try:
            self.downloader.download()
        except Exception, e:
            safe_print(e)
            traceback.print_exc()
            thread.exit()

    def kill(self):
        self.downloader.kill()

class JoinThread(threading.Thread):
    def __init__(self, store):
        Thread.__init__(self)
        self.daemon = True
        self.store = store
        
    def run(self):
        self.store.join()
        DHManager.all_is_done = True

class DHManager:
    '''
    manage download thread. try to brint up exited download thread if the total downloading job is not finished yet
    '''
    bringup_time = 30
    all_is_done = False
    def __init__(self, store, mem_inst, th_count):
        self.dhs = []
        self.original_count = th_count
        self.first_die_time = None
        self.store = store
        self.mem_inst = mem_inst
        self.exit = False
        self.killcmd_issued = False
        self.join_th = JoinThread(self.store)

        for i in range(0, th_count):
            self.dhs.append(DH(store, mem_inst))
            self.dhs[-1].start()

        self.join_th.start()

        safe_print("At %s, we are now downloading..." % (datetime.now().strftime(DATEFMT)))

    def wait_for_all_exit(self):
        while True:
            if len(self.dhs) == 0:
                break

            if self.first_die_time != None and (datetime.now() - self.first_die_time).seconds > DHManager.bringup_time:
                for i in range(len(self.dhs), self.original_count):
                    self.dhs.append(DH(self.store, self.mem_inst))
                    self.dhs[-1].start()
                self.first_die_time = None

            for dh in self.dhs:
                if not dh.is_alive():
                    self.dhs.remove(dh)
                    if self.first_die_time == None:
                        self.first_die_time = datetime.now()
    
            time.sleep(0.1)

    def kill(self):
        for dh in self.dhs:
            dh.kill()

        safe_print("%d thread need to be killed, please wait." % len(self.dhs))

        while True:
            for dh in self.dhs:
                if not dh.is_alive():
                    self.dhs.remove(dh)
                    sys.stdout.write(".")

            if len(self.dhs) == 0:
                break
            time.sleep(0.0001)
        
        safe_print("done")

class Spider:
    def __init__(self, url ,proxys, download_path):
        #signal.signal(signal.SIGINT, self.on_sigint)
	self.url = url
	self.start_time = datetime.now()
	self.proxys = proxys
        self.download_path = download_path
        try:
            self.store = Store(self.proxys , self.download_path)
        except StoreError, e:
            safe_print(e)
            sys.exit(1)
	
	self.store.add_black_filter("{image}", "\.css", "\.js","\.ico"
					"\.png","\.jpg","\.jpeg","\.gif")	

    def set_white(self,filter):
	self.store.add_white_filter(filter)
    
    def set_black(self,filter):
	self.store.add_black_filter(filter)

    def run(self):
	self.store.put(Job(self.url))
	mem_inst = Memory(self.download_path)
	dh_manager = None
        try:
            dh_manager = DHManager(self.store, mem_inst, 30)
            dh_manager.wait_for_all_exit()
        except KeyboardInterrupt:
            if dh_manager != None:
                dh_manager.kill() 		
    	self.end_time = datetime.now()
        safe_print("download finished, takes %s" % (self.end_time - self.start_time))

    def __del__(self):
	pass
    def on_sigint(self,signum, frame):
        os._exit(signum)

class spider_parse:
    def __init__(self):
	file = "download"
        dir = os.path.join(os.path.dirname(__file__),file)
	self.real_dir = dir
    
    def is_domain(self,url):
        pattern = re.compile(r'(?i)^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
        match = pattern.match(url)
        if match:
            return True
        else:
            return False

    def parse_url(self,data):
	result=[]
	return result
    
    def get_all_file(self,filepath,filelist):
        for file in os.listdir(filepath):
            real_file=os.path.join(filepath,file)
            if os.path.isfile(real_file):
		print real_file
                filelist.append(real_file)
	    elif os.path.isdir(real_file):
		self.get_all_file(real_file,filelist)
        return filelist

    def parse_data(self):
	result=[]
	filelist=[]
	self.get_all_file(self.real_dir,filelist)
	for file in filelist:
	    print file
	    file_object = open(file, 'r')
            try:
                data = file_object.read()
		result+=self.parse_url(data)
	    finally:
            	file_object.close()
	return result         

class Spider_one(object):
    def __init__(self,url):
	print "spider start"
	self.rescode = 0
	self.html = None
	self.result = []
	self.url = url
	self.res = None
	print "start connect...."
        try:
            socket.setdefaulttimeout(20)
            req = urllib2.Request(url)
	    req.add_header('Referer', 'http://tieba.baidu.com/')
            req.add_header('User-Agent',"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36")
	    self.res = urllib2.urlopen(req,timeout=10*60)
	    self.rescode = self.res.getcode()
	    self.html =  self.res.read()
	except urllib2.URLError, e:
	    self.html = None
	    print e.reason
	    print "connect failed"+url	
   	    pass
 
    def get_rescode(self):
	#200
	return self.rescode

    def get_html(self):
	return self.html

    def parse_html(self):
	return self.html

    def __del__(self):
        print "spider over"
	if self.res!=None:
	    self.res.close()
	    del self.res

if __name__ == '__main__':
    url = "https://www.cnblogs.com/"
    print url
    s = Spider_one(url)
    result=s.parse_html()
    print result

    s=Spider(url,"download")
    s.set_white("www\.cnblogs\.com")
    s.set_black('\.xml')
    s.run()

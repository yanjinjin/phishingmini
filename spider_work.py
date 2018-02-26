from getdomainbyurl import *
from spider import *
from spider_proxy import *
import os

class PhishtankBlackSpider(spider_parse):
    def __init__(self):
	file = "download/black/"
        dir = os.path.join(os.path.dirname(__file__),file)
	self.real_dir = os.path.join(dir , "data-phishtank-com")
	proxys = getProxys()
	s=Spider("http://data.phishtank.com/data/68b4c2263bc5687ad3f275f69de3dbba4ae5219aa88c349125d73a064260f866/online-valid.csv", proxys , dir)
        s.set_white("\.csv")
	s.run()
    
    def parse_data(self):
	result=[]
	filelist=[]
	self.get_all_file(self.real_dir,filelist)
	for file in filelist:
	    print file
	    file_object = open(file, 'r')
            try:
                text = file_object.readlines()
	        for line in text:
		    column = line.split(',')
		    result.append(column[1])
	    except:
                continue
	    finally:
            	file_object.close()
	return result 


class BlackSpider:
    def get_all_result(self):
        s = PhishtankBlackSpider()
        result=s.parse_data()
        return result


class AlexaGlobalSpider(spider_parse):
    def __init__(self):
	file = "download/white/"
        dir = os.path.join(os.path.dirname(__file__),file)
	self.real_dir = os.path.join(dir , "alexa-chinaz-com")
	proxys = getProxys()
	s=Spider("http://alexa.chinaz.com/Global/index.html",proxys,dir)
        s.set_white("alexa\.chinaz\.com/Global/index")
        s.set_white("alexa\.chinaz\.com/Language/index")
        s.set_white("alexa\.chinaz\.com/Country/index")
        s.set_white("alexa\.chinaz\.com/Category/index")
	s.run()
    
    def parse_url(self,data):
	result=[]
	host = data
	while 1:
            index_1 = host.find('<div class="righttxt"><h3><a href')
            if index_1 == -1:
                break
            host = host[index_1:]
            index_2 = host.find('</a><span>')
            if index_2 == -1:
                break
            index_2+=len('</a><span>')
            host = host[index_2:]
            index_3 = host.find('</span>')
            if index_3 == -1:
                break
            print host[:index_3]
            if self.is_domain(host[:index_3]):
                result.append(host[:index_3])
	return result

class WhiteSpider:
    def get_all_result(self):
        s = AlexaGlobalSpider()
        result=s.parse_data()
        return result

fw = open('white.txt', 'w')
d = SLD()
ws = WhiteSpider()
result = ws.get_all_result()
for i in result:
    print "%s\n////////////"%i
    host = d.get_second_level_domain(i)
    print host
    if host!="" and host!=None:
	fw.write(host+'\n')


fb = open('black.txt', 'w')
bs = BlackSpider()
result = bs.get_all_result()
for i in result:
    print "%s\n////////////"%i
    fb.write(i+'\n')

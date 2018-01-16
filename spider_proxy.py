#!/usr/bin/env python
# encoding: utf-8
from bs4 import BeautifulSoup
import urllib2
import time
import socket
import random

def is_open(ip,port):
    socket.setdefaulttimeout(2)
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        return True
    except Exception,e:
	print e ,ip ,port
        return False

def getContent(Url):
    """ Get the web site content.  """


    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}
    req = urllib2.Request(Url, headers=header)       # request

    while True:
        try:
            response = urllib2.urlopen(req).read()   # Web site content
            break
        except Exception as e:
            print 1, e
            time.sleep(random.choice(range(10, 20)))

    return response                        # The website content

def extractIPAddress(content):
    """ Extract web IP address and port. """
    proxys = []                                   # proxy list
    soup = BeautifulSoup(content, 'html.parser')  # soup object
    trs = soup.find_all('tr')                     # extract tr tag
    for tds in trs[1:]:
        td = tds.find_all('td')                   # extract td tag
	if str(td[5].contents[0]) != "HTTP":
	    continue
        if False == is_open(str(td[1].contents[0]) , str(td[2].contents[0])):
  	    continue
 
	proxys.append("http://"+str(td[1].contents[0]) + ":" + str(td[2].contents[0]))

    return proxys

def getProxys():
    """ main function. """
    Url = 'http://www.xicidaili.com/wt/1'   # assign relevant url
    content = getContent(Url)               # achieve html content
    proxys = extractIPAddress(content)      # achieve proxys
    return proxys
if  __name__ == "__main__":
    print getProxys()

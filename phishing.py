#coding=utf-8
import os
curdir = os.path.dirname(__file__)
import sys
sys.path.append(curdir) 
from bottle import route,request,template,view,run,Bottle,static_file,get, post, request 
from plog import *
from features import *
from bp import *
from weixin import *

@route('/static/js/<path>')  
def js(path):  
    return static_file(path, root='static/js/') 
 
@route('/static/css/<path>')  
def css(path):  
    return static_file(path, root='static/css/')  

@route('/static/img/<path>')
def css(path):
    return static_file(path, root='static/img/')

@route('/static/fonts/<path>')
def css(path):
    return static_file(path, root='static/fonts/')

@route('/',method = 'GET')
def index():
    browser = request.query.browser
    print browser
    return template('index', browser=browser)

@route('/index',method = 'GET')
def index2():
    browser = request.query.browser
    return template('index',browser = browser)

@route('/help',method = 'GET')
def help():
    return template('help')

@route('/check',method = 'POST')
def index_check():
    url = request.POST.get('url')
    score_not_phishing = 0 # -1
    score_phishing = 0 # 1
    score_suspect = 0 # 0
    if url == "" or url == None:
        return template('check',url=url , score_not_phishing=score_not_phishing , score_phishing=score_phishing , score_suspect=score_suspect)
    if not url.startswith("http"):
        return template('check',url=url , score_not_phishing=score_not_phishing , score_phishing=score_phishing , score_suspect=score_suspect)
    plog(url)
    url = url.strip()
    result = urlfeatureextractor(url)
    if result == []:
        return template('check',url=url , score_not_phishing=score_not_phishing , score_phishing=score_phishing , score_suspect=score_suspect)
    plog(result)
    result_bp = activate_bp(result)
    result_bp_float = float('%.2f' % result_bp[0])
    print result_bp_float
    if result_bp_float > 0:
        score_phishing = 100*result_bp_float
        if score_phishing > 100:
            score_phishing = 100
        score_suspect = 100 - score_phishing
    elif result_bp_float<0:
        score_not_phishing = 100*abs(result_bp_float)
        if score_not_phishing > 100:
           score_not_phishing = 100
        score_suspect = 100 - score_not_phishing
    print score_not_phishing,score_phishing,score_suspect
    return template('check',url=url , score_not_phishing=score_not_phishing , score_phishing=score_phishing , score_suspect=score_suspect)	

@route('/weixin',method = 'GET')
def weixin_get(self):
    search = web.input()
    signature=search.get('signature')
    timestamp=search.get('timestamp')
    nonce=search.get('nonce')
    echostr=search.get('echostr')
    print signature,timestamp,nonce,echostr
    wh = weixin_handle()
    re = wh.get(signature,timestamp,nonce,echostr)
    return re
@route('/weixin',method = 'POST')
def weixin_post(self):
    body = web.data()
    plog(body)
    wh = weixin_handle()
    re = wh.post(body)
    return re

build_bp()
#run(host='0.0.0.0',port=80)
# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))
import bottle
application = bottle.default_app()

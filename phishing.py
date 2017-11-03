#coding=utf-8
import os
curdir = os.path.dirname(__file__)
import sys
sys.path.append(curdir) 
import os,web
from plog import *
from features import *
from bp import *

web.config.debug = False

urls = (
    '/', 'index',
    '/index','index',
    '/check','check'
    )

t_globals = {  
    'datestr': web.datestr,  
    'cookie': web.cookies,  
}
render = web.template.render(os.path.join(curdir,'templates'), base='base', globals=t_globals)
app = web.application(urls, locals())

class index:
    def GET(self):
	search = web.input()
        browser = search.get('browser')
	return render.index(browser)

class check:
    def GET(self):
        raise web.seeother('index')
    def POST(self):
	search = web.input()
	url = search.get('url')
	score_not_phishing = 0 # -1
        score_phishing = 0 # 1
        score_suspect = 0 # 0
	if url == "" or url ==None:
	    return render.check(url , score_not_phishing , score_phishing , score_suspect)
	plog(url)
	url = url.strip()
	result = urlfeatureextractor(url)
	if result == []:
            return render.check(url , score_not_phishing , score_phishing , score_suspect)
	#plog(result)
	result_bp = activate_bp(result)
	result_bp_float = float('%.2f' % result_bp[0])
	#plog(result_bp_float)
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
	return render.check(url , score_not_phishing , score_phishing , score_suspect)	
	
if not __name__ == "__main__":    
    build_bp()
    application = app.wsgifunc()
else:
    build_bp()
    app.run()
	

% rebase('base.tpl')
%if browser == None or browser == '':
	<script type="text/javascript"> 
	var system ={}; 
		var p = navigator.platform;      
		system.win = p.indexOf("Win") == 0; 
		system.mac = p.indexOf("Mac") == 0; 
		system.x11 = (p == "X11") || (p.indexOf("Linux") == 0);    
		if(system.win||system.mac||system.xll){//pc
			window.location.href="/?browser=pc"; 
		}else{  
			window.location.href="/?browser=mobile"; 
		}
	</script>
%else:
	<div class="row">
		<div class="col-lg-12">
		<form class="form-search" id="myform" method="post" action="check">
			<input class="input-medium search-query" type="url" id= "url" name="url" placeholder="http(s)://" aria-describedby="basic-addon" maxlength="256" required/> 
			<button type="submit" class="btn btn-default" name="btn" value="check"><span class="glyphicon glyphicon-search">检测</span></button>
		</form>
		<p></p>
		<div class="carousel slide" id="carousel-55268">
			<div class="carousel-inner">
				<div class="item active">
				<p>本系统基于人工智能深度学习(BP神经网络)实现在线钓鱼网站检测(查询)，您可以在本系统检测钓鱼，诈骗等恶意网站，如果您遇到可疑网站，可把网址输入以上方框进行检测，避免造成您的损失！</p>	
				<p></p>
				<img alt="" src="/static/img/logo.jpg" />
				<p><a href="/help">帮助<span class="glyphicon glyphicon-arrow-right" aria-hidden="true"></span></a></p>
				%if browser == "pc":
					<div class="bdsharebuttonbox"><a href="#" class="bds_more" >分享到：</a><a href="#" class="bds_qzone" data-cmd="qzone" title="分享到QQ空间">QQ空间</a><a href="#" class="bds_tsina" data-cmd="tsina" title="分享到新浪微博">新浪微博</a><a href="#" class="bds_tqq" data-cmd="tqq" title="分享到腾讯微博">腾讯微博</a><a href="#" class="bds_renren" data-cmd="renren" title="分享到人人网">人人网</a><a href="#" class="bds_weixin" title="分享到微信">关注微信公众号：</a><img alt="" src="/static/img/weixin.jpg" height="100" width="100"/>
					</div>
					<script>window._bd_share_config={"common":{"bdSnsKey":{},"bdText":"","bdMini":"2","bdMiniList":false,"bdPic":"","bdStyle":"2","bdSize":"16"},"share":{"bdSize":16}};with(document)0[(getElementsByTagName('head')[0]||body).appendChild(createElement('script')).src='http://bdimg.share.baidu.com/static/api/js/share.js?v=89860593.js?cdnversion='+~(-new Date()/36e5)];</script>
				</div>
			</div>
		</div>
		</div>
	</div>
%end

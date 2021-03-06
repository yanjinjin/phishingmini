% rebase('base.tpl')
<div class="row">
    <div class="col-lg-12">    
	<p class="text-left"><strong><h4>网址：</h4></strong></p>
	<p class="text-left"><a href='{{ url }}'>{{ url }}</a></p>
	<p class="text-left"><strong><h4>检测结果：</h4></strong></p>
        <p class="text-left">以下结果仅供参考:(训练神经网络存在一个很小的误差，因此如下以百分比方式展示)</p>
	<p class="text-left">正常网站：</p>
        <div class="progress">
            <div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="{{ score_not_phishing }}" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: {{ score_not_phishing }}%">
            {{ score_not_phishing }}%
            </div>
        </div>
        <p class="text-left">疑似钓鱼网站：</p>
        <div class="progress">
            <div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="{{score_suspect}}" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: {{score_suspect}}%">
            {{score_suspect}}%
            </div>
        </div>
	<p class="text-left">钓鱼网站：</p>
        <div class="progress">
            <div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="{{score_phishing}}" aria-valuemin="0" aria-valuemax="100" style="min-width: 2em; width: {{score_phishing}}%">
            {{score_phishing}}%
            </div>
        </div>
	%if score_not_phishing ==0 and score_phishing ==0 and score_suspect ==0:
	    <p class="text-left">对不起! 网页无法正常访问，检测不到结果</p>
    </div>
</div>



<!DOCTYPE html>
<html lang="ja" prefix="og: http://ogp.me/ns#">
	<head>
		<meta name="robots" content="noindex,nofollow">
		<meta charset="utf-8">
		<title>メンテナンス情報 | DMM.com証券</title>
		<!--OGP用-->
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="DMM.com証券">
<meta property="og:title" content="DMM.com証券">
<meta property="og:description" content="DMM.com証券は「DMM.com証券だからできること」をテーマに、お客様のニーズに合わせた投資商品をご用意しております。(DMM FX、DMM CFD、DMMバヌーシー、DMM 株)">
<meta property="og:url" content="https://securities.dmm.com/">
<meta property="og:image" content="https://securities.dmm.com/_img/og/logo_ogp.png">
<meta property="og:type" content="article">
<!--Facebook用-->
<meta property="fb:app_id" content="1570045066342119">
<!--Twitter用-->
<meta name="twitter:card" content="summary_large_image">
		<script>
const ua = navigator.userAgent;
const SP = ua.indexOf('iPhone') > 0 || ua.indexOf('iPod') > 0 || ua.indexOf('Android') > 0 || ua.indexOf('iPad') > 0;
</script>
		<meta name="format-detection" content="telephone=no">
		<script src="/_js/jquery/jquery-3.2.0.min.js"></script>
		<script>
			if (SP) {
				// タブレット用コード
				// スマートフォン用コード
				document.write('<meta name="viewport" content="width=device-width,initial-scale=1">');
			} else {
				// PC用コード
			}
		</script>
		<meta name="description" content="">
		<script>
	if (ua.indexOf('iPhone') > 0 || ua.indexOf('iPod') > 0 || ua.indexOf('Android') > 0 && ua.indexOf('Mobile') > 0 || ua.indexOf('iPad') > 0 || ua.indexOf('Android') > 0) {
		// スマートフォン用コード
		// タブレット用コード
		document.write('<link rel="stylesheet" href="/_css' + window.location.pathname + 'detail.css?20240325" />');
	} else {
		// PC用コード
		document.write('<link rel="stylesheet" href="/_css' + window.location.pathname + 'detail_pc.css?20240325" />');
	}

</script>

<script>
	// メンテナンスデータを取得する関数を定義
	function fetchMaintenanceData() {
		// キャッシュを避けるため、ユニークなタイムスタンプ付きのクエリパラメータをURLに追加
		var cacheBuster = new Date().getTime();
		// var url = 'https://dev2.securities.dmm.com/fdata/maintenance.json?_=' + cacheBuster;
		var url = '/fdata/maintenance.json?_=' + cacheBuster;

		$.getJSON(url, function(data) {
			var content = data.data;

			// HTML要素としてコンテンツをパースし、テキストノードが空かどうかをチェック
			if ($('<div>').html(content).text().trim()) {
				// テキストノードに何か含まれている場合はコンテンツを表示
				$('#maintenance-title').html(data.title);
				$('#maintenance-content').html(content);
			} else {
				// 本文が空だった場合はhtmlの内容を表示
			}
		}).fail(function(jqXHR, textStatus, errorThrown) {
			// エラー処理
			console.error("メンテナンスデータの取得に失敗しました: " + textStatus, errorThrown);
			// $('#maintenance-content').addClass('u-tac').text('エラー時のテキスト');
		});
	}
	// ドキュメントの準備ができたら関数を呼び出す
	$(document).ready(function() {
		fetchMaintenanceData();
	});
</script>

<!-- tag_gtm -->
<script>
if (SP) {
// Google Tag Manager Tag No.220
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
											  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
	j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
		'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
					})(window,document,'script','dataLayer','GTM-P7XRSQR');
// Google Tag Manager Tag No.220
} else {
// Google Tag Manager Tag No.219
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
											  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
	j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
		'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
					})(window,document,'script','dataLayer','GTM-PX6R64G');
// Google Tag Manager Tag No.219
}
</script>
	</head>
	<body id="top">
		
		<header class="l-header l-header--fixed js-header">
	<div class="p-header">
		<h1 class="p-header__ttl"><a href="/"><img src="/_img/common/logo_sec.png" alt="DMM.com証券"></a></h1>
		<div class="c-hamburger js-hamburger" data-ua="sp">
			<span class="c-hamburger__line c-hamburger__line--1"></span>
			<span class="c-hamburger__line c-hamburger__line--2"></span>
			<span class="c-hamburger__line c-hamburger__line--3"></span>
		</div>
		<nav class="p-header__navi">
			<ul class="p-header__naviList">
				<li class="p-header__naviItem"><a href="/company/">会社概要<span data-ua="pc">About us</span></a></li>
				<li class="p-header__naviItem"><a href="https://dmmfx-holdings.com/" target="_blank">採用情報<span data-ua="pc">Recruit</span></a></li>
				<li class="p-header__naviItem"><a href="/finance-results/">財務状況等<span data-ua="pc">Finance results</span></a></li>
				<li class="p-header__naviItem"><a href="/support/">お客様サポート<span data-ua="pc">Support</span></a></li>
			</ul>
			<div class="p-header__naviBtn" data-ua="sp"><span class="c-closeBtn"></span>閉じる</div>
		</nav>
	</div>
</header>
		<main>
			<h1 class="c-title c-title--main">メンテナンス情報</h1>
			<div class="l-contents l-contents--gray">
				<section class="l-content p-maintenance__schedule" id="temporary-maintenance">
					<h2 class="c-title" id="maintenance-title">臨時システムメンテナンスまたはメンテナンスの延長について</h2>
					<div id="maintenance-content"><p class="u-tac">臨時メンテナンスまたはメンテナンス延長の予定はございません。</p></div>
				</section>
				<section class="l-content">
					<h2 class="c-title">定期メンテナンス時間</h2>
					<p class="c-text u-tac">定期メンテナンス情報につきましては下記よりご確認ください。</p>
					<div class="c-flexBox c-flexBox--c u-mt--30">
						<div class="c-flexBox__item">
							<a href="//fx.dmm.com/fx/session/" target="_blank" class="c-otherBtn c-otherBtn--fx">DMM FX</a>
						</div>
						<div class="c-flexBox__item">
							<a href="//fx.dmm.com/cfd/session/" target="_blank" class="c-otherBtn c-otherBtn--cfd">DMM CFD</a>
						</div>
						<div class="c-flexBox__item">
							<a href="//kabu.dmm.com/service/session/" target="_blank" class="c-otherBtn c-otherBtn--stock">DMM 株</a>
						</div>
					</div>
				</section>
			</div>
		</main>

		<span class="c-pageTop js-pageTop"><img src="/_img/toTop.png" alt="ページTOPへ"></span>
		<div class="c-lowerNaviWrap">
	<ul class="c-lowerNavi">
		<li class="c-lowerNavi__item"><a href="/">DMM.com証券<br data-ua="sp">トップ</a></li>
		<li class="c-lowerNavi__item"><a href="/company/">会社概要</a></li>
		<li class="c-lowerNavi__item"><a href="/support/">お問い合わせ</a></li>
	</ul>
</div>		<footer class="l-footer">
	<div class="p-footer">
		<!-- 外部リンク -->
		<div class="p-footer__inner">
			<ul class="p-footer__others">
				<li class="p-footer__othersList"><a href="https://www.fsa.go.jp/" target="_blank" class="c-footerLink">金融庁</a></li>
				<li class="p-footer__othersList"><a href="https://www.ffaj.or.jp/" target="_blank" class="c-footerLink">金融先物取引業協会</a></li>
				<li class="p-footer__othersList"><a href="https://www.fsa.go.jp/sesc/watch/index.html" target="_blank" class="c-footerLink">証券取引等監視委員会</a></li>
				<li class="p-footer__othersList"><a href="https://www.finmac.or.jp/" target="_blank" class="c-footerLink">証券・金融商品あっせん相談センター</a></li>
				<li class="p-footer__othersList"><a href="https://www.jsda.or.jp/" target="_blank" class="c-footerLink">日本証券業協会</a></li>
				<li class="p-footer__othersList"><a href="http://www.shouken-toukei.jp/" target="_blank" class="c-footerLink">証券統計ポータルサイト</a></li>
				<li class="p-footer__othersList"><a href="https://www.ffaj.or.jp/regulation/" target="_blank" class="c-footerLink">FX取引の規制について</a></li>
				<li class="p-footer__othersList"><a href="https://www.jsda.or.jp/about/hatten/inv_alerts/toushisagi/index.html" target="_blank" class="c-footerLink">株や社債をかたった投資詐欺にご用心！</a></li>
			</ul>
		</div>
		<!-- プライバシーマーク -->
		<div class="p-footer__inner">
			<div class="p-footer__bnr">
				<div class="p-footer__bnrItem">
					<a href="https://privacymark.jp/" target="_blank"><img src="/_img/pmark.gif" alt="Pマーク" class="c-img" lazyload="on"></a>
				</div>
			</div>
		</div>
		<!-- 商号等 加入協会等 -->
		<div class="p-footer__inner p-footer__inner--name">
			<dl class="p-footer__name">
				<dt class="p-footer__nameTtl">商号等：</dt>
				<dd class="p-footer__nameOutline">株式会社DMM.com証券 第一種金融商品取引業者/第二種金融商品取引業者　関東財務局長(金商)第1629号 商品先物取引業者</dd>
				<dt class="p-footer__nameTtl">加入協会等：</dt>
				<dd class="p-footer__nameOutline">日本証券業協会　日本投資者保護基金　一般社団法人金融先物取引業協会　日本商品先物取引協会　一般社団法人第二種金融商品取引業協会</dd>
			</dl>
			<p><a class="c-footerLink c-linkArrow" href="/notice/">金融商品取引法及び商品先物取引法に基づく表示</a></p>
		</div>
        <!-- 条項等 -->
		<div class="p-footer__inner p-footer__inner--terms">
			<ul class="p-footer__terms">
				<li class="p-footer__termsList"><a href="/privacy/" class="c-footerLink">個人情報保護宣言</a></li>
				<li class="p-footer__termsList"><a href="https://securities.dmm.com/policy/invitation/solicitation_policy.pdf" target="_blank" class="c-footerLink">勧誘方針</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/sairyou.pdf" target="_blank" class="c-footerLink">最良執行方針</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/naibutouroku.pdf" target="_blank" class="c-footerLink">内部者登録について</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/bosyu.pdf" target="_blank" class="c-footerLink">募集等に関わる株式等の顧客への配分に関わる基本方針</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/hansya.pdf" target="_blank" class="c-footerLink">反社会的勢力に対する基本方針</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/rieki.pdf" target="_blank" class="c-footerLink">利益相反管理方針の概要</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/specific.pdf" target="_blank" class="c-footerLink">「特定投資家、特定委託者、特定事業者」制度と移行に関わる「期限日」について</a></li>
				<li class="p-footer__termsList"><a href="/service_policy/" class="c-footerLink">お客様本位の業務運営に関する方針</a></li>
				<li class="p-footer__termsList"><a href="/important-sheet/" class="c-footerLink">重要情報シート(金融事業者編)</a></li>
				<li class="p-footer__termsList"><a href="/policy/compliance/" class="c-footerLink">コンプライアンス体制</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/moneyLaundering.pdf" target="_blank" class="c-footerLink">マネー・ローンダリング及びテロ資金供与対策に関する基本方針</a></li>
				<li class="p-footer__termsList"><a href="/fx_risk_disclosure/" class="c-footerLink">店頭FX取引に係るリスク情報に関する開示</a></li>
				<li class="p-footer__termsList"><a href="/security_policy/" class="c-footerLink">DMM.com証券のセキュリティポリシー</a></li>
				<li class="p-footer__termsList"><a href="/security_measures/" class="c-footerLink">お客様にお願いしたいセキュリティ対策</a></li>
				<li class="p-footer__termsList"><a href="/_pdf/cookie_policy.pdf" target="_blank" class="c-footerLink">Cookie(クッキー)ポリシー</a></li>
			</ul>
		</div>
		<div class="p-footer__inner p-footer__inner--notes">
			<div class="p-footer__notes">
				<p class="p-footer__notesList">当社Webサイトまたは取引ツール等における「アカウント」という表記は「口座」と同義です。あらかじめご了承ください。</p>
			</div>
		</div>
		<div class="c-copyright"><small>&copy; 2017 DMM.com Securities Co.,Ltd. All Rights Reserved.</small></div>
	</div>
</footer>
		<script src="/_js/common.js?20200916"></script>
		<script src="/_js/header.js"></script>
		<script>
			var ref = getQueryParameter('ref');
			if (ref === 'i') {
				$('.js-changeTxt').text('書類アップロード');
			}
		</script>
		<!--tag0156-->
<!-- Global site tag (gtag.js) - Google Ads: 984400895 -->
 <script async src="https://www.googletagmanager.com/gtag/js?id=AW-984400895"></script>
 <script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'AW-984400895');
 </script>
<!--//tag0156-->

<!--tag0157-->
<!-- Global site tag (gtag.js) - Google Ads: 961475481 -->
 <script async src="https://www.googletagmanager.com/gtag/js?id=AW-961475481"></script>
 <script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'AW-961475481');
 </script>
<!--//tag0157-->

<!--tag0160-->
<!-- Global site tag (gtag.js) - Google Ads: 10780534154 -->
<script async src=https://www.googletagmanager.com/gtag/js?id=AW-10780534154>
</script>
<script>
	window.dataLayer = window.dataLayer || [];
	function gtag(){dataLayer.push(arguments);}
	gtag('js', new Date());
	gtag('config', 'AW-10780534154');
</script>
<!--//tag0160-->

<!-- Tag No.237 -->
<script async src="https://s.yimg.jp/images/listing/tool/cv/ytag.js"></script>
<script>
window.yjDataLayer = window.yjDataLayer || [];
function ytag() { yjDataLayer.push(arguments); }
ytag({
  "type":"yss_retargeting",
  "config": {
    "yahoo_ss_retargeting_id": "1000135862",
    "yahoo_sstag_custom_params": {
    }
  }
});
</script>
<!--// Tag No.237 -->

<!-- Tag No.238 -->
<script async src="https://s.yimg.jp/images/listing/tool/cv/ytag.js"></script>
<script>
window.yjDataLayer = window.yjDataLayer || [];
function ytag() { yjDataLayer.push(arguments); }
ytag({
  "type":"yjad_retargeting",
  "config":{
    "yahoo_retargeting_id": "0BOD055YGW",
    "yahoo_retargeting_label": "",
    "yahoo_retargeting_page_type": "",
    "yahoo_retargeting_items":[
      {item_id: '', category_id: '', price: '', quantity: ''}
    ]
  }
});
</script>
<!--// Tag No.238 -->

<!--Tag No.0165-->
<!-- Twitter conversion tracking base code -->
<script>
	!function(e,t,n,s,u,a){e.twq||(s=e.twq=function(){s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);
	},s.version='1.1',s.queue=[],u=t.createElement(n),u.async=!0,u.src='https://static.ads-twitter.com/uwt.js',
	a=t.getElementsByTagName(n)[0],a.parentNode.insertBefore(u,a))}(window,document,'script');
	twq('config','nzm4z');
	</script>
	<!-- End Twitter conversion tracking base code -->
<!--//Tag No.0165-->

<!--   Tag No.A-44 -->
<script async src="https://s.yimg.jp/images/listing/tool/cv/ytag.js"></script>
<script>
window.yjDataLayer = window.yjDataLayer || [];
function ytag() { yjDataLayer.push(arguments); }
ytag({
  "type":"yss_retargeting",
  "config": {
    "yahoo_ss_retargeting_id": "1000419231",
    "yahoo_sstag_custom_params": {
    }
  }
});
</script>
<!-- //Tag No.A-44 -->
<!--   Tag No.A-47 -->
<!--   A-47はA-44の直下に設置 -->
<script async src="https://s.yimg.jp/images/listing/tool/cv/ytag.js"></script>
<script>
window.yjDataLayer = window.yjDataLayer || [];
function ytag() { yjDataLayer.push(arguments); }
ytag({
  "type":"yjad_retargeting",
  "config":{
    "yahoo_retargeting_id": "1HHW3CE4ZZ",
    "yahoo_retargeting_label": "",
    "yahoo_retargeting_page_type": "",
    "yahoo_retargeting_items":[
      {item_id: '', category_id: '', price: '', quantity: ''}
    ]
  }
});
</script>
<!-- //Tag No.A-47 -->

<!--Tag No.0167-->
<img src="https://a-mpd.com/pixel.png?own=c3b830f9a769b49d3250795223caad4d&agt=1fafa7253357262103a42a0fdc865bba&brnd=afc581ffd5443fb2ad47655b320f9b93&pg=2daba54cb820a940bb838d8f78eb7f7f" border="0" width="1" height="1" alt="" style="display:none;">
<!--//Tag No.0167-->

<!--Tag No.0170-->
<script type="text/javascript">
(function(s,m,n,l,o,g,i,c,a,d){c=(s[o]||(s[o]={}))[g]||(s[o][g]={});if(c[i])return;c[i]=function(){(c[i+"_queue"]||(c[i+"_queue"]=[])).push(arguments)};a=m.createElement(n);a.charset="utf-8";a.async=true;a.src=l;d=m.getElementsByTagName(n)[0];d.parentNode.insertBefore(a,d)})(window,document,"script","https://cd.ladsp.com/script/pixel2.js","Smn","Logicad","pixel");Smn.Logicad.pixel({
"f":"1",
"smnAdvertiserId":"00021696"});
(function(s,m,n,l,o,g,i,c,a,d){c=(s[o]||(s[o]={}))[g]||(s[o][g]={});if(c[i])return;c[i]=function(){(c[i+"_queue"]||(c[i+"_queue"]=[])).push(arguments)};a=m.createElement(n);a.charset="utf-8";a.async=true;a.src=l;d=m.getElementsByTagName(n)[0];d.parentNode.insertBefore(a,d)})(window,document,"script","https://cd.ladsp.com/script/pixel2_p_delay.js","Smn","Logicad","pixel_p_delay");
Smn.Logicad.pixel_p_delay({"smnDelaySecondsArray":[10,30,60,90],
"f":"1",
"smnAdvertiserId":"00021696"});
</script>
<!--//Tag No.0170-->

<!--tag0171-->
<!-- Google tag (gtag.js) --> 
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-16544428366"></script> 
<script> 
window.dataLayer = window.dataLayer || []; 
function gtag(){dataLayer.push(arguments);} 
gtag('js', new Date()); 
gtag('config', 'AW-16544428366'); 
</script>
<!--//tag0171-->
	</body>
</html>
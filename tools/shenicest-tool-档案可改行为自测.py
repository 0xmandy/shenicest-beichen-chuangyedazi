#!/usr/bin/env python3
# 创业搭子档案可改功能的行为自测。属于 shenicest 黑客松北辰命题，本脚本由 Claude 生成。
# 不看排版，只验状态机：默认行业、老档案兜底、阶段切换的连带重算、三处改行业互通、容器不被盖。
import io, os, subprocess, sys, tempfile, pathlib

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
HTML = ROOT / "shenicest-北辰-创业搭子-原型-Claude-2026-08-27.html"
CHROME = os.environ.get("CYD_CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
src = io.open(HTML, encoding="utf-8").read()

PROBE = r"""
var out = [];
window.onerror = function (m) { out.push('ERROR :: ' + m); };
setTimeout(function () {
  function ok(name, cond, got) { out.push((cond ? 'PASS' : 'FAIL') + ' :: ' + name + (cond ? '' : ' :: 实际=' + got)); }
  try {
  function guideEntries() { return (document.getElementById('taskGroups') || {}).innerHTML; }

  // A 默认行业
  ok('A 冷启动默认行业是人工智能', state.industry === '人工智能', state.industry);

  // B 老档案里 industry 是空串时兜回默认，不把默认冲掉
  try {
    localStorage.setItem('cydz_profile_v1', JSON.stringify({ v: 1, company: '已注册', industry: '' }));
    state.industry = '占位';
    var loaded = loadProfile();
    ok('B 老档案空行业兜回人工智能', loaded && state.industry === '人工智能', state.industry);
    localStorage.removeItem('cydz_profile_v1');
  } catch (e) { out.push('SKIP :: B 老档案兜底（localStorage 不可用）'); }

  // 从未注册起步
  state.company = '未注册'; state.industry = '人工智能'; state.graduation = ''; state.overseas = ''; state.finCond = [];
  finishOnboarding();
  // 首页那组入口从「猜您需要」改成「一条龙攻略」后就和档案解耦了，四个方块固定不变。
  // 这两条断言守的是「解耦没被改回去」，不是「入口跟着档案变」。
  var guideBefore = guideEntries();
  ok('C1 首页攻略入口渲染出来了', guideBefore.indexOf('guide-card') >= 0, '空的');
  ok('C2 未注册时问候语是未来创业者', document.getElementById('homeGreeting').textContent.indexOf('未来创业者') >= 0,
     document.getElementById('homeGreeting').textContent);
  var riskBefore = riskProfile().bars.length;

  // C 在我的页把阶段改成已注册，连带全部重算
  switchTab('profile');
  setProfileField(null, 'company', '已注册');
  ok('C3 阶段改成已注册', state.company === '已注册', state.company);
  ok('C4 首页攻略入口不随档案变', guideEntries() === guideBefore, '跟着档案变了');
  ok('C5 问候语跟着变回创业者', document.getElementById('homeGreeting').textContent.indexOf('未来创业者') < 0,
     document.getElementById('homeGreeting').textContent);
  ok('C6 风险维度换成已注册那一套', riskProfile().bars.length !== riskBefore, riskProfile().bars.length);
  try {
    var saved = JSON.parse(localStorage.getItem('cydz_profile_v1') || '{}');
    ok('C7 阶段改动落盘', saved.company === '已注册', saved.company);
  } catch (e) { out.push('SKIP :: C7 落盘（localStorage 不可用）'); }
  ok('C8 我的页那行文案跟着变', document.getElementById('profileFields').innerHTML.indexOf('企业阶段：已注册') >= 0, '没变');

  // D 我的页改行业，政策匹配结果跟着变
  var aiStrong = matchPolicies().strong.map(function (p) { return p.id; }).join(',');
  setProfileField(null, 'industry', '医药健康');
  ok('D1 行业改成医药健康', state.industry === '医药健康', state.industry);
  ok('D2 高匹配名单确实换了一批', matchPolicies().strong.map(function (p) { return p.id; }).join(',') !== aiStrong, '和人工智能时一模一样');
  ok('D3 高匹配里确有医药健康条目',
     matchPolicies().strong.some(function (p) { return (p.tags || []).indexOf('医药健康') >= 0; }), '没有');

  // E 找机会页改行业，那一页当场重渲染
  switchTab('opportunity');
  setIndustry('智能机器人');
  var oppHtml = document.getElementById('oppScroll').innerHTML;
  ok('E1 找机会页改行业生效', state.industry === '智能机器人', state.industry);
  ok('E2 找机会页选中态是智能机器人',
     oppHtml.indexOf('pol-chip on" onclick="setIndustry(\'智能机器人\')') >= 0, '选中态没跟上');

  // F 金融页开着时改行业，别把金融页盖成政策页
  openServiceDetail('金融服务');
  var titleBefore = document.getElementById('pageTitle').textContent;
  setIndustry('数据要素');
  var titleAfter = document.getElementById('pageTitle').textContent;
  ok('F1 金融页开着改行业不被政策页盖掉', titleAfter === titleBefore && titleAfter.indexOf('政策匹配') < 0,
     titleBefore + ' -> ' + titleAfter);
  closeServicePage();

  // G 融资条件两处共用同一份
  switchTab('profile');
  setProfileField(null, 'finCond', '有知识产权');
  ok('G1 我的页勾上融资条件', (state.finCond || []).indexOf('有知识产权') >= 0, JSON.stringify(state.finCond));
  switchTab('opportunity');
  // 找机会页 v7 拆成三栏后，融资条件的 chips 落在金融机会那一栏，先切过去再看
  setOppTab('fin');
  ok('G2 找机会页同步到选中态',
     document.getElementById('oppScroll').innerHTML.indexOf('pol-chip on" onclick="toggleFinCond(\'有知识产权\')') >= 0, '没同步');
  toggleFinCond('有知识产权');
  ok('G3 找机会页取消，我的页也取消', (state.finCond || []).indexOf('有知识产权') < 0, JSON.stringify(state.finCond));

  // I 能领的钱那一栏（v7 新增）。守的是排序主键、折叠区、金额口径三件事，
  // 这三样出错截图上全看不出来，只有断言逮得到。
  setOppTab('money');
  var moneyHtml = function () { return document.getElementById('oppScroll').innerHTML; };
  ok('I1 能领的钱栏渲染出补贴卡', moneyHtml().indexOf('openSubsidyDetail(') >= 0, '一张都没有');

  var ms = matchSubsidy();
  ok('I2 补贴条数是 44 笔', ms.all.length === 44, ms.all.length);
  ok('I3 申报窗口三态都算得出',
     ms.all.filter(x => x._win.st === 'open').length > 0 && ms.all.filter(x => x._win.st === 'unknown').length > 0,
     JSON.stringify(ms.all.map(x => x._win.st).filter((v, i, a) => a.indexOf(v) === i)));

  // 默认排序主键是能不能报，不是金额。第一张不该是那条 1 亿的落地奖励
  var firstReady = sortSubsidy(ms.all.filter(x => x._win.st !== 'closed'), 'ready')[0];
  ok('I4 默认排序把能报的排在前面', firstReady._win.st === 'open', firstReady.id + ' ' + firstReady._win.st);
  var firstMoney = sortSubsidy(ms.all.filter(x => x._win.st !== 'closed'), 'money')[0];
  ok('I5 切成按金额时第一张确实是金额最大的',
     firstMoney.capWan === Math.max.apply(null, ms.all.filter(x => x._win.st !== 'closed').map(x => x.capWan)),
     firstMoney.id + ' ' + firstMoney.capWan);

  // 已截止的默认收在折叠区里，展开才出现
  var closedId = ms.closed.length ? ms.closed[0].id : '';
  ok('I6 已截止的默认不在第一屏', !closedId || moneyHtml().indexOf("openSubsidyDetail('" + closedId + "')") < 0, closedId + ' 露出来了');
  if (closedId) {
    toggleSubFold();
    ok('I7 展开折叠区后已截止的出现', moneyHtml().indexOf("openSubsidyDetail('" + closedId + "')") >= 0, '展开了还是没有');
    toggleSubFold();
  }

  // 换行业，匹配理由要跟着重算
  setIndustry('医药健康');
  var med = matchSubsidy().all.filter(x => x.tag === '医药健康')[0];
  ok('I8 换行业后医药健康条目认出行业', med && med._reasons.join('').indexOf('行业：医药健康') >= 0,
     med ? med._reasons.join(' / ') : '库里没有医药健康条目');

  // 金额只能来自数据，界面不许自己算出一个数
  var capOK = SUBSIDY_ITEMS.every(function (s) { return typeof s.capWan === 'number'; });
  ok('I9 每条都有金额排序值', capOK, '有条目缺 capWan');

  // J 够不够得着的判定（v7 第二轮新增）。守的是「不硬判」与「判了要判对」两件事。
  state.company = '已注册'; state.industry = '人工智能';
  state.regPlace = ''; state.founded = ''; state.staff = ''; state.quals = [];
  switchTab('opportunity'); setOppTab('money');
  ok('J1 档案没填全时不摆判定，只给入口', !subsidyProfileReady()
     && document.getElementById('oppScroll').innerHTML.indexOf('sub-ask-btn') >= 0, '没给入口');

  // 填成朝阳区、成立 1-3 年、2-10 人、还没有任何资质
  setProfileField(null, 'regPlace', '朝阳区');
  setProfileField(null, 'founded', '1-3年');
  setProfileField(null, 'staff', '2-10人');
  ok('J2 三项填全后判定生效', subsidyProfileReady(), '还是没齐');

  var byId = {};
  matchSubsidy().all.forEach(function (x) { byId[x.id] = x; });
  ok('J3 朝阳区企业对朝阳区条目判符合', byId['CY-DATA-01']._fit.st === 'pass', byId['CY-DATA-01']._fit.st);
  ok('J4 朝阳区企业对经开区条目判不符合', byId['BDA-01']._fit.st === 'no', byId['BDA-01']._fit.st);
  ok('J5 不符合时说得出为什么', byId['BDA-01']._fit.why.join('').indexOf('经开区') >= 0, byId['BDA-01']._fit.why.join(''));
  ok('J6 没资质时要资质的条目判差一项', byId['BJ-GJJ-23']._fit.st === 'gap', byId['BJ-GJJ-23']._fit.st);
  ok('J7 原文没写门槛的照实标注不硬判', byId['CY-AI-01']._fit.st === 'unknown', byId['CY-AI-01']._fit.st);

  // 拿到专精特新之后，差一项那条要翻成符合
  setProfileField(null, 'quals', '专精特新中小企业');
  var after = {}; matchSubsidy().all.forEach(function (x) { after[x.id] = x; });
  ok('J8 补上资质后判定跟着翻', after['BJ-GJJ-23']._fit.st === 'pass', after['BJ-GJJ-23']._fit.st);

  // 人数超限要判不符合
  setProfileField(null, 'staff', '500人以上');
  var big = {}; matchSubsidy().all.forEach(function (x) { big[x.id] = x; });
  ok('J9 人数超限判不符合', big['BJ-VOUCHER-02']._fit.st === 'no', big['BJ-VOUCHER-02']._fit.st);
  setProfileField(null, 'staff', '2-10人');

  // 未注册时要独立法人的条目判不符合，收创业团队的那几条不受影响
  setProfileField(null, 'company', '未注册');
  var un = {}; matchSubsidy().all.forEach(function (x) { un[x.id] = x; });
  ok('J10 未注册时要法人资格的判不符合', un['CY-DATA-01']._fit.st === 'no', un['CY-DATA-01']._fit.st);
  ok('J11 收创业团队的条目不受未注册影响', un['BJ-GJJ-21']._fit.st !== 'no', un['BJ-GJJ-21']._fit.st);

  // 能领的钱那栏顶上的解锁对照条，三个数是现算的。这里守住它和 judgeSubsidy 同一个口径：
  // 界面上「开完公司解锁 N 笔」用的是 gate 字段直接数，判定结果用的是 judgeSubsidy，
  // 两者对不上就说明有一边改了另一边没跟上，界面会摆出一个判定支撑不了的数字。
  var unAll = matchSubsidy().all;
  var lockedN = SUBSIDY_ITEMS.filter(function (x) { var g = x.gate || {}; return !g.teamOK && (g.legal || g.reg); }).length;
  var judgedNo = unAll.filter(function (x) { return x._fit.st === 'no'; }).length;
  ok('J15 解锁对照条的笔数与判定结果同口径', lockedN === judgedNo, lockedN + ' vs ' + judgedNo);
  ok('J16 未注册时现在就能报的至少有一笔',
     unAll.filter(function (x) { return x._fit.st === 'pass' && x._win.st === 'open'; }).length >= 1,
     unAll.filter(function (x) { return x._fit.st === 'pass' && x._win.st === 'open'; }).length);

  setProfileField(null, 'company', '已注册');

  // 默认排序主键是够不够得着
  var ms2 = matchSubsidy();
  var firstFit = sortSubsidy(ms2.all.filter(x => x._win.st !== 'closed'), 'fit')[0];
  ok('J12 默认排序把你符合的排最前', firstFit._fit.st === 'pass', firstFit.id + ' ' + firstFit._fit.st);
  ok('J13 每条都写了判不了的部分', SUBSIDY_ITEMS.every(x => x.gate && x.gate.beyond), '有条目 beyond 是空的');
  ok('J14 设了硬门槛的都有原文依据',
     SUBSIDY_ITEMS.every(x => !(x.gate.reg || x.gate.legal || (x.gate.quals || []).length) || x.gateFrom),
     '有条目设了门槛却没依据');

  // H 重设档案后行业回到默认而不是空
  resetOnboarding();
  ok('H1 重设档案后行业回默认', state.industry === '人工智能', state.industry);
  } catch (e) { out.push('ERROR :: 探针中途抛异常 :: ' + (e && e.message ? e.message : e)); }

  var d = document.createElement('div');
  d.id = 'CYDTEST';
  // 标记运行时拼出来，否则 dump 出的 DOM 里探针自己这段源码也会被搜到（README 记过这个坑）
  d.textContent = ['CYD', 'RESULT'].join('') + '<<' + out.join(' ;; ') + '>>';
  d.style.cssText = 'position:fixed;left:-9999px';
  document.body.appendChild(d);
}, 700);
"""

page = src.replace("</body>", "<script>%s</script></body>" % PROBE, 1)
tmp = pathlib.Path(tempfile.mkdtemp(prefix="cydtest-"))
target = tmp / "behavior.html"
io.open(target, "w", encoding="utf-8").write(page)

# 无头 Chrome dump 完常常不退，直接 wait 会一直挂着（README 已知坑）。
# 后台跑，轮询到探针那一行真写出来了就往下走，别拿文件存不存在当完成信号。
import time
domfile = tmp / "dom.html"
profile_dir = tmp / "prof"
with io.open(domfile, "w", encoding="utf-8") as fh:
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=6000",
         "--allow-file-access-from-files", "--dump-dom",
         "--user-data-dir=%s" % profile_dir, "file://%s" % target],
        stdout=fh, stderr=subprocess.DEVNULL)
    dom = ""
    for _ in range(45):
        time.sleep(2)
        try:
            dom = io.open(domfile, encoding="utf-8").read()
        except Exception:
            dom = ""
        if "CYDRESULT<<" in dom and ">>" in dom.split("CYDRESULT<<", 1)[1]:
            break
    proc.kill()
subprocess.run(["pkill", "-f", "user-data-dir=%s" % profile_dir], capture_output=True)

# dump 出来的 DOM 会把 << >> 转义成 &lt;&lt; &gt;&gt;，两种写法都认
import html as htmllib
head, tail = ("CYDRESULT&lt;&lt;", "&gt;&gt;") if "CYDRESULT&lt;&lt;" in dom else ("CYDRESULT<<", ">>")
start = dom.find(head)
if start < 0:
    print("探针没跑出来。dump 落在 %s，%d 字节" % (domfile, len(dom)))
    print("页面里有没有探针的 div：%s" % ("有" if "CYDTEST" in dom else "没有"))
    sys.exit(2)
body = htmllib.unescape(dom[start + len(head):dom.find(tail, start)])
lines = [x.strip() for x in body.split(";;") if x.strip()]
fails = [x for x in lines if x.startswith("FAIL")]
print("===== 档案可改功能行为自测 =====")
for line in lines:
    print(" ", line)
print("===== %d 条，失败 %d 条 =====" % (len(lines), len(fails)))
sys.exit(1 if fails else 0)

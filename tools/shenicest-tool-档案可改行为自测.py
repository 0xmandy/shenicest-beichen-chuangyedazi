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
  function hasKaiGongSi() { return (document.getElementById('taskGroups') || {}).innerHTML.indexOf('开公司') >= 0; }

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
  ok('C1 未注册时首页有开公司入口', hasKaiGongSi(), '没有');
  ok('C2 未注册时问候语是未来创业者', document.getElementById('homeGreeting').textContent.indexOf('未来创业者') >= 0,
     document.getElementById('homeGreeting').textContent);
  var riskBefore = riskProfile().bars.length;

  // C 在我的页把阶段改成已注册，连带全部重算
  switchTab('profile');
  setProfileField(null, 'company', '已注册');
  ok('C3 阶段改成已注册', state.company === '已注册', state.company);
  ok('C4 开公司入口收起来了', !hasKaiGongSi(), '还在');
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
  ok('G2 找机会页同步到选中态',
     document.getElementById('oppScroll').innerHTML.indexOf('pol-chip on" onclick="toggleFinCond(\'有知识产权\')') >= 0, '没同步');
  toggleFinCond('有知识产权');
  ok('G3 找机会页取消，我的页也取消', (state.finCond || []).indexOf('有知识产权') < 0, JSON.stringify(state.finCond));

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

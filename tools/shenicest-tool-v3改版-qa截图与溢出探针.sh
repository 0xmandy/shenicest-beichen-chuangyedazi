#!/bin/zsh
# 排版自查：每个状态各生成一张测试页，并行跑截图与 dump-dom 溢出探针。
# 属于 shenicest 黑客松北辰命题「创业搭子」，本脚本由 Claude 生成。
#
# 用法：在 repo 里直接 zsh tools/shenicest-tool-v3改版-qa截图与溢出探针.sh
# 路径全部从 repo 推出来，不写死任何人的机器路径：
#   CYD_HTML    要测的原型 html，默认 repo 根目录那份
#   CYD_QA_DIR  截图与 dump 的落地目录，默认 repo 下的 qa-out/（已进 .gitignore）
ROOT="${0:A:h:h}"
CYD_HTML="${CYD_HTML:-$ROOT/shenicest-北辰-创业搭子-原型-Claude-2026-08-27.html}"
SP="${CYD_QA_DIR:-$ROOT/qa-out}"
CHROME="${CYD_CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[[ -f "$CYD_HTML" ]] || { echo "找不到原型 html：$CYD_HTML"; exit 1; }
[[ -x "$CHROME" ]] || { echo "找不到 Chrome：$CHROME，用 CYD_CHROME=... 指过来"; exit 1; }
export CYD_HTML
setopt null_glob          # 首次跑 qa-out 是空的，别让 rm 的通配符 no matches found
mkdir -p "$SP"
cd "$SP"
rm -f shot-*.png dom-*.html t-*.html
gen () {
  python3 - "$1" "$2" "$3" <<'PY'
import io,os,sys
name,h,js = sys.argv[1],sys.argv[2],sys.argv[3]
src = io.open(os.environ["CYD_HTML"], encoding="utf-8").read()
src = src.replace("</head>", "<style>.phone-shell{max-height:none!important;height:%spx!important;border-radius:0!important;border:none!important}.page-overlay.active,.chat-overlay.active{position:absolute}</style></head>" % h, 1)
probe = """
setTimeout(function(){
  var bad=[];
  document.querySelectorAll('#app *').forEach(function(el){
    if(el.scrollWidth - el.clientWidth > 2 && el.clientWidth > 0 &&
       getComputedStyle(el).overflowX !== 'auto' && getComputedStyle(el).overflowX !== 'scroll'){ bad.push(el.className || el.tagName); }
  });
  var d=document.createElement('div');
  d.textContent='QAOVERFLOW['+(bad.length? bad.slice(0,12).join(' | ') : 'none')+']';
  d.style.cssText='position:fixed;left:-9999px';
  document.body.appendChild(d);
},900);
"""
src = src.replace("</body>", "<script>setTimeout(function(){ %s },200);%s</script></body>" % (js, probe), 1)
io.open("t-%s.html" % name, "w", encoding="utf-8").write(src)
PY
}
gen onboard 900 ""
gen home 1150 "state.company='已注册';state.industry='智能机器人';finishOnboarding();"
gen company 2000 "state.company='已注册';finishOnboarding();switchTab('company');"
gen risk 1400 "state.company='已注册';finishOnboarding();openRiskPage();"
gen chat 1100 "state.company='已注册';finishOnboarding();openChat();"
# 老周的第三个知识源：办事流程回答卡。直接渲染，绕开 respond 里的随机延时
gen chat-task 1900 "state.company='已注册';finishOnboarding();openChat();addRichMessage(taskAnswerHTML('社保'));addRichMessage(taskAnswerHTML('app'));"
gen t-shebao 1700 "state.company='已注册';finishOnboarding();openTaskPage('社保');"
gen t-kaigongsi 1500 "state.company='已注册';finishOnboarding();openTaskPage('开公司');"
gen t-aigc 2400 "state.company='已注册';finishOnboarding();openTaskPage('aigc');"
gen t-app 1400 "state.company='已注册';finishOnboarding();openTaskPage('app');"
gen t-baoshui 1450 "state.company='已注册';finishOnboarding();openTaskPage('报税');"
gen policy 1700 "state.company='已注册';state.industry='智能机器人';finishOnboarding();openServiceDetail('政策补贴');"
gen fin 1700 "state.company='已注册';state.finCond=['有知识产权'];finishOnboarding();openServiceDetail('金融服务');"
gen opp 1700 "state.company='已注册';state.industry='智能机器人';state.finCond=['有知识产权'];finishOnboarding();switchTab('opportunity');"
gen cal 1400 "state.company='已注册';finishOnboarding();openServiceDetail('行政日历');"
# 我的页的企业档案五项可改，收起态与展开态都要看。展开态挑融资条件那一项，它八个选项最长，最容易撑破
gen profile 1500 "state.company='已注册';finishOnboarding();switchTab('profile');"
gen profile-open 1700 "state.company='已注册';state.finCond=['有知识产权','有跨境结算需求'];finishOnboarding();switchTab('profile');toggleProfileField('finCond');"
NAMES=(onboard:900 home:1150 company:2000 risk:1400 chat:1100 chat-task:1900 t-shebao:1700 t-kaigongsi:1500 t-aigc:2400 t-app:1400 t-baoshui:1450 policy:1700 fin:1700 opp:1700 cal:1400 profile:1500 profile-open:1700)
for n in $NAMES; do
  nm=${n%%:*}; ht=${n##*:}
  rm -rf /tmp/cyd-$nm /tmp/cydd-$nm 2>/dev/null
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 --window-size=440,$ht --user-data-dir=/tmp/cyd-$nm --screenshot="shot-$nm.png" "file://$SP/t-$nm.html" >/dev/null 2>&1 &
  "$CHROME" --headless=new --disable-gpu --virtual-time-budget=4000 --dump-dom --window-size=440,$ht --user-data-dir=/tmp/cydd-$nm "file://$SP/t-$nm.html" > "dom-$nm.html" 2>/dev/null &
done

# 无头 Chrome 出图之后进程常常不退，直接 wait 会一直挂着。轮询到产物齐了就往下走。
# 别拿「文件在不在」当完成信号：重定向一开就把 dom-*.html 建出来了，此时里面还是空的，
# 照这个判断会提前 pkill，把一半的 dump 掐断。要认探针真写出来的那一行。
want=${#NAMES[@]}
for i in {1..90}; do
  got=$(grep -lE "QAOVERFLOW\[[^']" dom-*.html 2>/dev/null | wc -l | tr -d ' ')
  pics=$(ls -l shot-*.png 2>/dev/null | awk '$5>0' | wc -l | tr -d ' ')
  [[ "$got" -ge "$want" && "$pics" -ge "$want" ]] && break
  sleep 2
done
sleep 1
pkill -f "user-data-dir=/tmp/cyd" 2>/dev/null

# grep 结果时要滤掉探针自己的源码：dump 出来的 DOM 里既有那段 script 原文、也有它写出来的隐藏 div
echo "===== 横向溢出探针 ====="
bad=0
for f in dom-*.html; do
  r=$(grep -o "QAOVERFLOW\[[^]]*\]" "$f" | grep -v "bad.length" | head -1)
  printf "%-22s %s\n" "${f#dom-}" "${r:-探针没跑出来}"
  [[ "$r" == "QAOVERFLOW[none]" ]] || bad=$((bad+1))
done
echo "===== 截图在 $SP/shot-*.png ====="
# 冷启动页那一条是团队原始 demo 自带的 30px 溢出，被 phone-shell 的 overflow:hidden 兜住。
# 判断是不是自己引入的，先拿改动前的备份跑同一个探针对比，别直接开修。
echo "非 none 的状态数：$bad（冷启动页 onboard 属于已知项）"

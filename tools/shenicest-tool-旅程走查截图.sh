#!/bin/zsh
# 四条用户旅程的走查截图。属于 shenicest 黑客松北辰命题「创业搭子」，本脚本由 Claude 生成。
#
# 与 shenicest-tool-v3改版-qa截图与溢出探针.sh 的分工：那个是排版自查（每个页面各一张 + 溢出探针），
# 这个是按旅程顺序取图，给交付物「用户旅程图与走查」用，落在 qa-out/journey/。
#
# 用法：zsh tools/shenicest-tool-旅程走查截图.sh
#   CYD_HTML       要测的原型 html，默认 repo 根目录那份
#   CYD_JOURNEY_DIR 截图落地目录，默认 repo 下 qa-out/journey/
ROOT="${0:A:h:h}"
CYD_HTML="${CYD_HTML:-$ROOT/shenicest-北辰-创业搭子-原型-Claude-2026-08-27.html}"
SP="${CYD_JOURNEY_DIR:-$ROOT/qa-out/journey}"
CHROME="${CYD_CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[[ -f "$CYD_HTML" ]] || { echo "找不到原型 html：$CYD_HTML"; exit 1; }
[[ -x "$CHROME" ]] || { echo "找不到 Chrome：$CHROME，用 CYD_CHROME=... 指过来"; exit 1; }
export CYD_HTML
setopt null_glob
mkdir -p "$SP"
cd "$SP"
rm -f shot-*.png t-*.html

# 生成测试页：把手机壳拉高到指定高度，末尾注入驱动脚本
gen () {
  python3 - "$1" "$2" "$3" <<'PY'
import io,os,sys
name,h,js = sys.argv[1],sys.argv[2],sys.argv[3]
src = io.open(os.environ["CYD_HTML"], encoding="utf-8").read()
src = src.replace("</head>", "<style>.phone-shell{max-height:none!important;height:%spx!important;border-radius:0!important;border:none!important}.page-overlay.active,.chat-overlay.active{position:absolute}</style></head>" % h, 1)
src = src.replace("</body>", "<script>setTimeout(function(){ %s },200);</script></body>" % js, 1)
io.open("t-%s.html" % name, "w", encoding="utf-8").write(src)
PY
}

REG="state.company='已注册';state.industry='智能机器人';finishOnboarding();"
NEW="state.company='未注册';finishOnboarding();"
STMT="今天终于拿到营业执照了，公司注册在北辰智汇谷，接下来要开银行基本户和税务登记。"

# 旅程一 选身份 → 办事 → 开公司
gen j1-onboard        900  ""
gen j1-home          1500  "$NEW"
gen j1-company       2600  "$NEW switchTab('company');"
gen j1-kaigongsi     2200  "$NEW openTaskPage('开公司');"
gen j1-kaigongsi-reg 2200  "$NEW openTaskPage('开公司');setTimeout(function(){pickStep('开公司',1);},300);"

# 旅程二 小事广场 → 日历
gen j2-plaza         2200  "$REG switchTab('circle');"
gen j2-st-input      1700  "$REG openSmallThing();"
gen j2-st-confirm    1900  "$REG openSmallThing();stFill('$STMT');stSubmit();"
gen j2-cal           1700  "$REG openSmallThing();stFill('$STMT');stSubmit();setTimeout(function(){stConfirm();openServiceDetail('行政日历');},1800);"

# 旅程三 管公司 → 政府补助
gen j3-policy        2000  "$REG openServiceDetail('政策补贴');"
gen j3-policy-detail 1900  "$REG openServiceDetail('政策补贴');setTimeout(function(){var m=matchPolicies();var p=(m.strong&&m.strong[0])||(m.related&&m.related[0]);if(p)openPolicyDetail(p.id);},400);"

# 旅程四 问老周 → 政策库检索
gen j4-chat          1700  "$REG openChat();"
gen j4-chat-policy    2000  "$REG openChat();setTimeout(function(){addMessage('我能申报什么补贴','user');addRichMessage(policyAnswerHTML('我能申报什么补贴'));},400);"

NAMES=(j1-onboard:900 j1-home:1500 j1-company:2600 j1-kaigongsi:2200 j1-kaigongsi-reg:2200 \
       j2-plaza:2200 j2-st-input:1700 j2-st-confirm:1900 j2-cal:1700 \
       j3-policy:2000 j3-policy-detail:1900 j4-chat:1700 j4-chat-policy:2000)

# user-data-dir 放在输出目录底下，不写 /tmp：沙箱里跑时 /tmp 是拦着的，
# Chrome 起不来又不报错，只会安静地不出图。
# 串行跑。十几个无头 Chrome 一起起会全军覆没，一张图都不写，而且不报错。
# 每起一个就等它把图写出来，再杀掉进程起下一个。
rm -rf .cd-* 2>/dev/null
for n in $NAMES; do
  nm=${n%%:*}; ht=${n##*:}
  # 驱动里有嵌套 setTimeout（最长 1800ms），virtual-time 给足 8 秒
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=8000 \
    --window-size=440,$ht --user-data-dir="$SP/.cd-$nm" \
    --screenshot="$SP/shot-$nm.png" "file://$SP/t-$nm.html" >/dev/null 2>&1 &
  for i in {1..25}; do
    [[ -s "$SP/shot-$nm.png" ]] && break
    sleep 1
  done
  # 无头 Chrome 截完图进程不退，图写完就可以杀，产物已经落地
  pkill -f "user-data-dir=$SP/.cd-$nm" 2>/dev/null
  printf "."
done
echo
rm -rf .cd-* 2>/dev/null

echo "===== 旅程截图 $SP ====="
for n in $NAMES; do
  nm=${n%%:*}
  sz=$(ls -l shot-$nm.png 2>/dev/null | awk '{print $5}')
  printf "%-20s %s\n" "$nm" "${sz:-没出图}"
done

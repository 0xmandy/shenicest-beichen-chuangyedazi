# -*- coding: utf-8 -*-
"""第一趟：CSS token、新组件样式、SVG 图标雪碧图、tab 栏、首页、管公司页。
每一处都用唯一锚点定位，锚点匹配不到或匹配多次就报错退出，不做静默跳过。"""
import io, sys, os

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-2026-08-27.html"
src = io.open(PATH, encoding="utf-8").read()

def rep(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit("锚点[%s]命中 %d 次，应为 1 次，退出" % (label, n))
    src = src.replace(old, new, 1)
    print("  ok  %s" % label)

def repn(old, new, times, label):
    """预期命中 times 次，全部替换"""
    global src
    n = src.count(old)
    if n != times:
        sys.exit("锚点[%s]命中 %d 次，应为 %d 次，退出" % (label, n, times))
    src = src.replace(old, new)
    print("  ok  %s（%d 处）" % (label, times))

def cut(start, end, new, label):
    """把 start 锚点开始、到 end 锚点之前（不含 end）的整段换成 new"""
    global src
    if src.count(start) != 1 or src.count(end) != 1:
        sys.exit("区间锚点[%s]不唯一，退出" % label)
    i = src.index(start); j = src.index(end)
    if j <= i:
        sys.exit("区间锚点[%s]顺序不对，退出" % label)
    src = src[:i] + new + src[j:]
    print("  ok  %s" % label)

# ============================================================
# 1. 设计 token：旧变量名全部保留成别名，2400 行既有 CSS 不用动就换了皮
# ============================================================
OLD_ROOT = """        :root {
            --primary: #FF6B35;
            --primary-light: #FFF0EA;
            --primary-dark: #E5532B;
            --bg: #F8F6F3;
            --card: #FFFFFF;
            --text: #2D2D2D;
            --text-secondary: #8B8B8B;
            --text-light: #B8B8B8;
            --border: #EEEAE5;
            --success: #4CAF50;
            --warning: #FFB300;
            --danger: #F44336;
            --info: #42A5F5;
            --shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.1);
            --radius: 16px;
            --radius-sm: 10px;
            --radius-xs: 8px;
            --tab-height: 64px;
            --header-height: 52px;
            --safe-top: env(safe-area-inset-top, 0px);
            --safe-bottom: env(safe-area-inset-bottom, 0px);
            --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
        }"""

NEW_ROOT = """        /* ===== 设计 token =====
           橙管机会与行动，蓝灰管证据与边界，风险三档单独一组。
           末尾保留旧变量名当别名，既有样式不改一行就跟着换皮。 */
        :root {
            /* 中性九阶 */
            --n0: #FFFFFF;
            --n50: #FAF8F6;
            --n100: #F2EFEB;
            --n200: #E7E2DC;
            --n300: #D5CFC7;
            --n400: #B3ADA4;
            --n500: #8C877F;
            --n700: #4A4640;
            --n900: #26231F;
            /* 品牌橙：机会、行动、进度 */
            --brand: #E5532B;
            --brand-bright: #FF6B35;
            --brand-100: #FFE0D2;
            --brand-50: #FFF3EE;
            /* 信任蓝灰：证据、原文、数据边界 */
            --trust: #23557A;
            --trust-600: #2E6A96;
            --trust-100: #D7E4EF;
            --trust-50: #EDF3F8;
            /* 风险三档 */
            --risk-high: #D64545;
            --risk-high-bg: #FBEBEB;
            --risk-mid: #C97A00;
            --risk-mid-bg: #FDF4E5;
            --risk-low: #2F8F5B;
            --risk-low-bg: #EAF5EE;
            /* 字号阶梯 */
            --fs-cap: 11px;
            --fs-sm: 12px;
            --fs-body: 13px;
            --fs-md: 14px;
            --fs-lg: 16px;
            --fs-xl: 18px;
            --fs-num: 22px;
            /* 间距阶梯 */
            --sp-1: 4px;
            --sp-2: 6px;
            --sp-3: 8px;
            --sp-4: 12px;
            --sp-5: 16px;
            --sp-6: 20px;
            --sp-7: 24px;
            /* 圆角阶梯 */
            --r-xs: 8px;
            --r-sm: 12px;
            --r-md: 16px;
            --r-lg: 20px;
            --r-pill: 999px;
            /* 两级阴影 + 一条描边。次卡用描边不用阴影，层级才分得开 */
            --sh-1: 0 1px 2px rgba(38,35,31,.04), 0 2px 8px rgba(38,35,31,.05);
            --sh-2: 0 6px 24px rgba(38,35,31,.10);
            --hair: 1px solid var(--n200);

            /* 旧变量名别名 */
            --primary: var(--brand);
            --primary-light: var(--brand-50);
            --primary-dark: #C6421E;
            --bg: var(--n50);
            --card: var(--n0);
            --text: var(--n900);
            --text-secondary: var(--n500);
            --text-light: var(--n400);
            --border: var(--n200);
            --success: var(--risk-low);
            --warning: var(--risk-mid);
            --danger: var(--risk-high);
            --info: var(--trust-600);
            --shadow: var(--sh-1);
            --shadow-lg: var(--sh-2);
            --radius: var(--r-md);
            --radius-sm: var(--r-sm);
            --radius-xs: var(--r-xs);
            --tab-height: 64px;
            --header-height: 52px;
            --safe-top: env(safe-area-inset-top, 0px);
            --safe-bottom: env(safe-area-inset-bottom, 0px);
            --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
        }"""
rep(OLD_ROOT, NEW_ROOT, "设计 token")

# 页面外底色跟着中性阶走
rep("            background: #E8E4DF;\n", "            background: #E4DFD9;\n", "壳外底色")

# ============================================================
# 2. 五大场景覆盖的样式整块删（第 3 件事要求连样式一起删）
# ============================================================
rep("""        /* ===== 首页看板：五大场景与三段清单（搬自 coze 有数_demo）===== */
        .scenario-bar { background:var(--card); border-radius:var(--radius); padding:12px 14px; margin:0 20px 12px; box-shadow:var(--shadow); }
        .scenario-bar-title { font-size:12px; font-weight:600; color:var(--text); margin-bottom:8px; }
        .scenario-tags { display:flex; flex-wrap:wrap; gap:6px; }
""",
    """        /* ===== 首页看板：三段清单（搬自 coze 有数_demo）===== */
""", "删五大场景样式")

# 快捷入口九宫格样式整块删，换成办事入口（第 2 件事）
rep("""        .quick-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            padding: 0 20px 16px;
            flex-shrink: 0;
        }
        .quick-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            padding: 12px 6px;
            border-radius: var(--radius-sm);
            background: var(--card);
            box-shadow: var(--shadow);
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        .quick-item:active {
            transform: scale(0.9);
        }
        .quick-item .qi-icon {
            font-size: 24px;
            line-height: 1;
        }
        .quick-item .qi-label {
            font-size: 11px;
            color: var(--text-secondary);
            font-weight: 500;
            text-align: center;
        }
""", "", "删快捷入口九宫格样式")

rep("""            .quick-grid {
                gap: 6px;
            }
""", """            .task-grid {
                gap: 8px;
            }
""", "小屏适配改指办事入口")

# feature-banner 样式删（为您推荐下面那两条 banner 的专属样式）
old_fb_start = "        .feature-banner {"
i = src.index(old_fb_start)
j = src.index("        .section-header", i) if "        .section-header" in src[i:] else -1
# 用更稳的方式：找到 .feature-banner 段落结束（下一个不以 .feature-banner/.fb- 开头的顶层选择器）
seg = src[i:]
end_marker = None
for m in ["\n        .section-header {", "\n        /* ", "\n        .service-", "\n        .board-"]:
    p = seg.find(m, 1)
    if p > 0 and (end_marker is None or p < end_marker):
        end_marker = p
if end_marker is None:
    sys.exit("找不到 feature-banner 样式段结尾")
print("  ok  删 feature-banner 样式（%d 字符）" % end_marker)
src = src[:i] + src[i+end_marker+1:]

# ============================================================
# 3. 新组件样式：图标、三级卡、证据组件、过渡态、办事入口、管公司分栏
# ============================================================
NEW_CSS = """
        /* ============================================================
           新增组件层（本轮视觉重做）
           1 图标 2 三级卡收敛 3 证据与数据边界 4 过渡态 5 办事入口 6 管公司分栏
           ============================================================ */

        /* --- 1 图标：全部内联 SVG symbol，零外部请求，跨系统同一形状 --- */
        .ic {
            width: 1em; height: 1em; display: inline-block; flex: 0 0 auto;
            fill: none; stroke: currentColor; stroke-width: 1.75;
            stroke-linecap: round; stroke-linejoin: round;
            vertical-align: -0.14em;
        }
        .ic-16 { width: 16px; height: 16px; }
        .ic-18 { width: 18px; height: 18px; }
        .ic-20 { width: 20px; height: 20px; }
        .ic-22 { width: 22px; height: 22px; }
        .ic-26 { width: 26px; height: 26px; }
        .ic-40 { width: 40px; height: 40px; stroke-width: 1.4; }

        .tab-item .tab-icon { display: flex; align-items: center; justify-content: center; height: 23px; }
        .tab-item .tab-icon .ic { width: 23px; height: 23px; color: var(--n500); transition: color .2s, stroke-width .2s; }
        .tab-item.active .tab-icon .ic { color: var(--brand); stroke-width: 2.15; }
        .tab-item.active .tab-icon { transform: none; }

        /* --- 2 三级卡：主卡有阴影，次卡只描边，列表项只分隔线 --- */
        .card-main { background: var(--n0); border-radius: var(--r-md); padding: var(--sp-5); box-shadow: var(--sh-1); }
        .card-sub  { background: var(--n0); border-radius: var(--r-sm); padding: 13px 14px; border: var(--hair); box-shadow: none; }
        .row-item  { padding: 11px 14px; border-bottom: var(--hair); }
        .row-item:last-child { border-bottom: none; }

        /* 既有的七八套卡按三级归位，改样式不改渲染函数 */
        .pol-card, .fin-card, .rk-card {
            border: var(--hair); box-shadow: none; border-radius: var(--r-sm);
        }
        .rk-card { border-left-width: 3px; }
        .rk-card.high   { border-left-color: var(--risk-high); }
        .rk-card.medium { border-left-color: var(--risk-mid); }
        .rk-card.low    { border-left-color: var(--risk-low); }
        .board-list, .timeline-card, .cal-card { border: var(--hair); box-shadow: none; }
        .board-progress, .st-card, .rk-grade, .pol-industry, .chat-entry { box-shadow: var(--sh-1); }
        .st-card { border: var(--hair); }
        .st-num.st-warn { color: var(--risk-mid); }
        .st-num.st-ok { color: var(--risk-low); }
        .pol-level { color: var(--brand); background: var(--brand-50); }
        .pol-badge-act { background: var(--risk-low-bg); color: var(--risk-low); }
        .pol-badge-hi { background: var(--brand-50); color: var(--brand); }
        .fin-org { color: var(--trust); background: var(--trust-50); }
        .rk-lv.high   { background: var(--risk-high-bg); color: var(--risk-high); }
        .rk-lv.medium { background: var(--risk-mid-bg);  color: var(--risk-mid); }
        .rk-lv.low    { background: var(--risk-low-bg);  color: var(--risk-low); }
        .rk-grade-v.high   { background: var(--risk-high-bg); color: var(--risk-high); }
        .rk-grade-v.medium { background: var(--risk-mid-bg);  color: var(--risk-mid); }
        .rk-grade-v.low    { background: var(--risk-low-bg);  color: var(--risk-low); }
        .bd-level.high { background: var(--risk-high-bg); color: var(--risk-high); }
        .bd-level.mid  { background: var(--risk-mid-bg);  color: var(--risk-mid); }
        .rk-fill.low { background: var(--risk-low); }
        .rk-fill.medium { background: var(--risk-mid); }
        .rk-fill.high { background: var(--risk-high); }
        .rk-tag.low { color: var(--risk-low); }
        .rk-tag.medium { color: var(--risk-mid); }
        .rk-tag.high { color: var(--risk-high); }
        .sop-step.done { background: var(--risk-low-bg); color: var(--risk-low); }
        .alert-warning { background: var(--risk-mid-bg); color: #8A5A00; border-left-color: var(--risk-mid); }
        .alert-info { background: var(--trust-50); color: var(--trust); border-left-color: var(--trust-600); }
        .alert-danger { background: var(--risk-high-bg); color: var(--risk-high); border-left-color: var(--risk-high); }
        .alert-card .alert-icon { display: flex; align-items: center; }
        .pol-hero { background: linear-gradient(135deg, var(--brand-bright), var(--brand)); }
        .bp-fill, .fab, .confirm-btn { background: linear-gradient(135deg, var(--brand-bright), var(--brand)); }
        .fab { box-shadow: 0 6px 20px rgba(229,83,43,.38); }

        /* --- 3 证据与数据边界：产品的卖点，给它专属的蓝灰体系 --- */
        .ev-badge {
            display: inline-flex; align-items: center; gap: 4px;
            font-size: 10px; font-weight: 600; line-height: 1.6;
            padding: 2px 7px; border-radius: var(--r-xs);
            background: var(--trust-50); color: var(--trust);
            border: 1px solid var(--trust-100);
        }
        .ev-badge.ev-derived { background: var(--n100); color: var(--n700); border-color: var(--n200); }
        .ev-badge.ev-none    { background: var(--n50);  color: var(--n500); border-color: var(--n200); }
        .ev-badge.ev-lib     { background: var(--brand-50); color: var(--brand); border-color: var(--brand-100); }
        .ev-bar {
            display: flex; align-items: center; gap: 6px;
            margin: 10px -14px -13px; padding: 8px 14px;
            background: var(--trust-50); border-top: 1px solid var(--trust-100);
            border-radius: 0 0 var(--r-sm) var(--r-sm);
            font-size: 10px; color: var(--trust); line-height: 1.5;
        }
        .ev-bar .ev-go { margin-left: auto; font-weight: 600; flex: 0 0 auto; }
        .ev-panel {
            margin: 14px 20px 20px; padding: 13px 15px;
            background: var(--n0); border: var(--hair);
            border-left: 3px solid var(--trust); border-radius: var(--r-sm);
        }
        .ev-panel-t {
            display: flex; align-items: center; gap: 6px;
            font-size: var(--fs-body); font-weight: 700; color: var(--trust); margin-bottom: 9px;
        }
        .ev-line { display: flex; gap: 8px; margin-bottom: 7px; }
        .ev-line:last-child { margin-bottom: 0; }
        .ev-key {
            flex: 0 0 auto; font-size: 10px; font-weight: 700; line-height: 1.7;
            padding: 1px 6px; border-radius: 5px; height: fit-content;
            background: var(--trust-50); color: var(--trust);
        }
        .ev-line.k-none .ev-key { background: var(--n100); color: var(--n700); }
        .ev-val { font-size: var(--fs-cap); color: var(--n700); line-height: 1.75; }
        /* 通用流程口径横幅：命题方没给数据的页面必须顶着它 */
        .ev-generic {
            display: flex; gap: 9px; align-items: flex-start;
            margin: 14px 20px 12px; padding: 11px 13px;
            background: var(--n100); border: 1px dashed var(--n300); border-radius: var(--r-sm);
        }
        .ev-generic .ic { color: var(--n500); margin-top: 1px; }
        .ev-generic-t { font-size: var(--fs-sm); font-weight: 700; color: var(--n700); }
        .ev-generic-d { font-size: var(--fs-cap); color: var(--n500); line-height: 1.7; margin-top: 3px; }
        .demo-tag {
            display: inline-flex; align-items: center; gap: 3px;
            font-size: 10px; font-weight: 600; padding: 1px 6px;
            border-radius: 5px; background: var(--n100); color: var(--n500);
            border: 1px solid var(--n200);
        }

        /* --- 4 过渡态：空、加载中、判定过程 --- */
        .state-empty {
            display: flex; flex-direction: column; align-items: center; gap: 9px;
            margin: 0 20px 14px; padding: 26px 18px; text-align: center;
            background: var(--n0); border: 1px dashed var(--n300); border-radius: var(--r-sm);
        }
        .state-empty .ic { color: var(--n300); }
        .state-empty-t { font-size: var(--fs-sm); color: var(--n500); line-height: 1.75; }
        .state-empty-b { font-size: var(--fs-sm); font-weight: 600; color: var(--brand); background: var(--brand-50); border-radius: var(--r-pill); padding: 7px 16px; }
        .state-loading { display: flex; align-items: center; gap: 9px; margin: 0 20px 12px; padding: 13px 14px; background: var(--n0); border: var(--hair); border-radius: var(--r-sm); }
        .state-loading .sl-dots { display: flex; gap: 4px; }
        .state-loading .sl-dots i { width: 6px; height: 6px; border-radius: 50%; background: var(--brand); opacity: .25; animation: slPulse 1.1s infinite ease-in-out; }
        .state-loading .sl-dots i:nth-child(2) { animation-delay: .18s; }
        .state-loading .sl-dots i:nth-child(3) { animation-delay: .36s; }
        @keyframes slPulse { 0%,100% { opacity:.25; transform:scale(.85);} 45% { opacity:1; transform:scale(1);} }
        .state-loading-t { font-size: var(--fs-sm); color: var(--n500); }
        /* 判定过程：竖线串起来的证据链，方块勾选从空到满 */
        .ai-steps { position: relative; padding: 12px 0 4px 4px; }
        .ai-steps::before { content: ''; position: absolute; left: 11px; top: 20px; bottom: 14px; width: 1px; background: var(--n200); }
        .ai-step { position: relative; display: flex; align-items: flex-start; gap: 11px; font-size: var(--fs-body); color: var(--n400); padding: 8px 0; transition: color .3s; line-height: 1.6; }
        .ai-step.done { color: var(--n900); }
        .ai-dot {
            position: relative; z-index: 1; width: 15px; height: 15px; border-radius: 4px;
            background: var(--n0); border: 1.5px solid var(--n300); flex: 0 0 auto; margin-top: 2px;
            display: flex; align-items: center; justify-content: center; transition: all .3s;
        }
        .ai-dot.done { background: var(--trust); border-color: var(--trust); }
        .ai-dot::after { content: ''; width: 6px; height: 3px; border-left: 1.6px solid #fff; border-bottom: 1.6px solid #fff; transform: rotate(-45deg) scale(0); transition: transform .25s; margin-top: -1px; }
        .ai-dot.done::after { transform: rotate(-45deg) scale(1); }

        /* --- 5 首页办事入口：用户嘴里说得出来的话，不按部门分 --- */
        .task-head { display: flex; align-items: baseline; gap: 8px; padding: 2px 20px 10px; }
        .task-head h3 { font-size: var(--fs-lg); font-weight: 700; color: var(--n900); }
        .task-head span { font-size: var(--fs-cap); color: var(--n500); }
        .task-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 0 20px 16px; }
        .task-card {
            display: flex; flex-direction: column; gap: 7px;
            background: var(--n0); border: var(--hair); border-radius: var(--r-md);
            padding: 13px 12px 11px; cursor: pointer;
            transition: transform .2s cubic-bezier(.25,.46,.45,.94), border-color .2s;
        }
        .task-card:active { transform: scale(.96); border-color: var(--brand-100); }
        .task-card.tk-top { border-color: var(--brand-100); background: linear-gradient(180deg, var(--brand-50), var(--n0) 58%); }
        .task-ic {
            width: 34px; height: 34px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            background: var(--n100); color: var(--n700);
        }
        .task-card.tk-top .task-ic { background: var(--brand-100); color: var(--brand); }
        .task-t { font-size: var(--fs-md); font-weight: 700; color: var(--n900); line-height: 1.35; }
        .task-d { font-size: var(--fs-cap); color: var(--n500); line-height: 1.55; min-height: 2.2em; }
        .task-foot { display: flex; align-items: center; }

        /* --- 6 管公司页：经营事项 / 合规风险两栏 --- */
        .cm-seg { display: flex; gap: 8px; margin: 0 20px 12px; flex-shrink: 0; }
        .cm-seg-i {
            flex: 1; position: relative; text-align: center; font-size: var(--fs-body);
            padding: 9px 0; border-radius: var(--r-sm); background: var(--n0);
            color: var(--n500); border: var(--hair);
        }
        .cm-seg-i.on { background: var(--n900); color: var(--n0); border-color: var(--n900); font-weight: 600; }
        .cm-seg-badge {
            display: none; margin-left: 5px; min-width: 16px; height: 16px; padding: 0 4px;
            border-radius: 8px; background: var(--risk-high); color: #fff;
            font-size: 9px; font-weight: 700; line-height: 16px;
        }
        .cm-seg-badge.on { display: inline-block; }
        .more-toggle {
            display: flex; align-items: center; gap: 6px;
            margin: 2px 20px 12px; padding: 11px 14px;
            background: var(--n0); border: var(--hair); border-radius: var(--r-sm);
            font-size: var(--fs-body); color: var(--n700); font-weight: 600;
        }
        .more-toggle .mt-sub { font-weight: 400; font-size: var(--fs-cap); color: var(--n500); }
        .more-toggle .ic { margin-left: auto; color: var(--n400); transition: transform .25s; }
        .more-toggle.open .ic { transform: rotate(90deg); }

        /* --- 办事详情页里的步骤清单 --- */
        .tp-lead { margin: 0 20px 12px; font-size: var(--fs-body); color: var(--n700); line-height: 1.8; }
        .tp-steps { margin: 0 20px 14px; background: var(--n0); border: var(--hair); border-radius: var(--r-sm); overflow: hidden; }
        .tp-step { display: flex; gap: 11px; padding: 12px 14px; border-bottom: var(--hair); }
        .tp-step:last-child { border-bottom: none; }
        .tp-no {
            flex: 0 0 auto; width: 20px; height: 20px; border-radius: 6px;
            background: var(--n100); color: var(--n700);
            font-size: 11px; font-weight: 700; line-height: 20px; text-align: center; margin-top: 1px;
        }
        .tp-t { font-size: var(--fs-md); font-weight: 600; color: var(--n900); line-height: 1.45; }
        .tp-d { font-size: var(--fs-sm); color: var(--n500); line-height: 1.7; margin-top: 3px; }
        .tp-cta {
            margin: 0 20px 14px; padding: 13px; text-align: center;
            background: var(--brand); color: #fff; font-size: var(--fs-md); font-weight: 600;
            border-radius: var(--r-sm); display: flex; align-items: center; justify-content: center; gap: 7px;
        }
        .tp-note { margin: 0 20px 14px; font-size: var(--fs-cap); color: var(--n500); line-height: 1.8; }
        .tp-park { margin: 0 20px 10px; padding: 13px 14px; background: var(--n0); border: var(--hair); border-radius: var(--r-sm); }
        .tp-park-n { font-size: var(--fs-md); font-weight: 600; color: var(--n900); }
        .tp-park-d { font-size: var(--fs-sm); color: var(--n500); line-height: 1.7; margin-top: 4px; }
</style>"""
rep("    </style>", NEW_CSS, "追加新组件样式")

# ============================================================
# 4. SVG 雪碧图：53 个线性图标，统一 24 视框、1.75 描边、currentColor
# ============================================================
ICONS = {
 "home": '<path d="M3.2 10.6 12 3.4l8.8 7.2"/><path d="M5.6 9.4V19.6a1.4 1.4 0 0 0 1.4 1.4h10a1.4 1.4 0 0 0 1.4-1.4V9.4"/><path d="M9.6 21v-5.6h4.8V21"/>',
 "company": '<path d="M3 21h18"/><path d="M5 21V5.6a1.4 1.4 0 0 1 1.4-1.4h6.2a1.4 1.4 0 0 1 1.4 1.4V21"/><path d="M14 10.4h4.6A1.4 1.4 0 0 1 20 11.8V21"/><path d="M8 8.4h2.6M8 12.4h2.6M8 16.4h2.6M16.6 14.6h1.2M16.6 18h1.2"/>',
 "target": '<circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="4.3"/><circle cx="12" cy="12" r="1.1" fill="currentColor" stroke="none"/>',
 "plaza": '<path d="M3.4 6.4A1.4 1.4 0 0 1 4.8 5h8.8a1.4 1.4 0 0 1 1.4 1.4v4.8a1.4 1.4 0 0 1-1.4 1.4H8.2L5 15.2v-2.6a1.4 1.4 0 0 1-1.6-1.4Z"/><path d="M17.8 8.8h1.4a1.4 1.4 0 0 1 1.4 1.4v5a1.4 1.4 0 0 1-1.4 1.4h-.4v2.6l-3.2-2.6h-4.2"/>',
 "biz": '<path d="M4 9.4h16V19a1.4 1.4 0 0 1-1.4 1.4H5.4A1.4 1.4 0 0 1 4 19Z"/><path d="M3.2 9.4 5 4.6h14l1.8 4.8"/><path d="M9.8 20.4v-5.2h4.4v5.2"/>',
 "shield": '<path d="M12 3.4 5.2 6.2v5.4c0 4.2 2.8 7.6 6.8 9 4-1.4 6.8-4.8 6.8-9V6.2Z"/><path d="M9.2 12.1l2 2 3.6-3.9"/>',
 "receipt": '<path d="M6 3.4h12v17.2l-2.4-1.6-2.4 1.6-2.4-1.6-2.4 1.6L6 19.2Z"/><path d="M9.4 8.2h5.2M9.4 11.8h5.2M9.4 15.4h3"/>',
 "doc": '<path d="M7 3.4h6.6L18 8v12.6H7Z"/><path d="M13.4 3.4V8H18"/><path d="M9.8 12.4h5.4M9.8 16h4"/>',
 "coin": '<circle cx="12" cy="12" r="8.4"/><path d="M9 8.6 12 12.6l3-4"/><path d="M12 12.6V17"/><path d="M9.4 13.2h5.2M9.4 15.2h5.2"/>',
 "award": '<circle cx="12" cy="9" r="5.2"/><path d="M8.6 13.6 7.4 21l4.6-2.4 4.6 2.4-1.2-7.4"/>',
 "pin": '<path d="M12 21s6.4-5.6 6.4-10.4A6.4 6.4 0 0 0 5.6 10.6C5.6 15.4 12 21 12 21Z"/><circle cx="12" cy="10.4" r="2.4"/>',
 "users": '<path d="M15.6 20.2v-1.8a3.6 3.6 0 0 0-3.6-3.6H7.2a3.6 3.6 0 0 0-3.6 3.6v1.8"/><circle cx="9.6" cy="7.6" r="3.4"/><path d="M20.4 20.2v-1.8a3.6 3.6 0 0 0-2.7-3.5"/><path d="M15.4 4.3a3.6 3.6 0 0 1 0 6.6"/>',
 "calendar": '<rect x="3.6" y="5.2" width="16.8" height="15.2" rx="1.8"/><path d="M3.6 9.8h16.8M8.4 3.4v3.4M15.6 3.4v3.4"/>',
 "alert": '<path d="M10.6 4.2 3.4 17.4a1.6 1.6 0 0 0 1.4 2.4h14.4a1.6 1.6 0 0 0 1.4-2.4L13.4 4.2a1.6 1.6 0 0 0-2.8 0Z"/><path d="M12 9.6v4M12 17.2h.01"/>',
 "file": '<path d="M13.4 3.4H7a1.6 1.6 0 0 0-1.6 1.6v14a1.6 1.6 0 0 0 1.6 1.6h10a1.6 1.6 0 0 0 1.6-1.6V8.6Z"/><path d="M13.4 3.4v5.2h5.2"/><path d="M8.8 13h6.4M8.8 16.6h4.4"/>',
 "external": '<path d="M14 4.4h5.6V10"/><path d="M19.6 4.4 11.4 12.6"/><path d="M17.6 13.6v5A1.6 1.6 0 0 1 16 20.2H5.8A1.6 1.6 0 0 1 4.2 18.6V8.4a1.6 1.6 0 0 1 1.6-1.6h5"/>',
 "check": '<path d="M4.8 12.6 9.6 17.4 19.2 6.8"/>',
 "plus": '<path d="M12 5v14M5 12h14"/>',
 "search": '<circle cx="10.8" cy="10.8" r="6.4"/><path d="M15.6 15.6 20 20"/>',
 "chevron": '<path d="M9.4 5.6 15.8 12l-6.4 6.4"/>',
 "bolt": '<path d="M13.4 2.8 4.6 13.6h6.2l-.8 7.6 8.8-10.8h-6.2Z"/>',
 "lock": '<rect x="4.8" y="10.4" width="14.4" height="9.8" rx="1.8"/><path d="M8.2 10.4V7.8a3.8 3.8 0 0 1 7.6 0v2.6"/>',
 "chat": '<path d="M20.4 11.6a7.4 7.4 0 0 1-8 7.4c-.9 0-1.8-.15-2.6-.44L4.2 20.4l1.9-5.4A7.4 7.4 0 1 1 20.4 11.6Z"/>',
 "user": '<circle cx="12" cy="8.2" r="3.8"/><path d="M4.8 20.2a7.2 7.2 0 0 1 14.4 0"/>',
 "close": '<path d="M6 6l12 12M18 6 6 18"/>',
 "clock": '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.2V12l3.2 2"/>',
 "spark": '<path d="M12 3.4 13.7 9l5.6 1.7-5.6 1.7L12 18l-1.7-5.6L4.7 10.7 10.3 9Z"/><path d="M18.8 3.2v2.8M20.2 4.6h-2.8"/>',
 "bank": '<path d="M3.6 9.6 12 4.4l8.4 5.2"/><path d="M5.8 9.6v8.2M10 9.6v8.2M14 9.6v8.2M18.2 9.6v8.2"/><path d="M3.6 20.2h16.8"/>',
 "chart": '<path d="M4.2 20.2V4.4"/><path d="M4.2 20.2h15.6"/><path d="M7.8 16.6V12M12 16.6V7.6M16.2 16.6v-6.4"/>',
 "globe": '<circle cx="12" cy="12" r="8.4"/><path d="M3.6 12h16.8"/><path d="M12 3.6a13 13 0 0 1 0 16.8 13 13 0 0 1 0-16.8Z"/>',
 "heart": '<path d="M12 20.2s-7.4-4.6-7.4-9.6A4.2 4.2 0 0 1 12 8.2a4.2 4.2 0 0 1 7.4 2.4c0 5-7.4 9.6-7.4 9.6Z"/>',
 "trophy": '<path d="M8 4.4h8v5a4 4 0 0 1-8 0Z"/><path d="M8 5.6H5.2v1.6a3 3 0 0 0 2.8 3"/><path d="M16 5.6h2.8v1.6a3 3 0 0 1-2.8 3"/><path d="M12 13.4v3.4M8.6 20.4h6.8"/>',
 "edit": '<path d="M15.4 4.6a1.9 1.9 0 0 1 2.7 2.7L8.4 17l-3.6 1 1-3.6Z"/><path d="M4.6 20.6h14.8"/>',
 "question": '<circle cx="12" cy="12" r="8.4"/><path d="M9.6 9.4a2.5 2.5 0 0 1 4.9.6c0 1.7-2.5 2.5-2.5 2.5"/><path d="M12 16.4h.01"/>',
 "bell": '<path d="M17.6 10.6a5.6 5.6 0 0 0-11.2 0c0 5-2 6.4-2 6.4h15.2s-2-1.4-2-6.4Z"/><path d="M13.4 20a1.7 1.7 0 0 1-2.8 0"/>',
 "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2.6v2.4M12 19v2.4M21.4 12H19M5 12H2.6M18.6 5.4l-1.7 1.7M7.1 16.9l-1.7 1.7M18.6 18.6l-1.7-1.7M7.1 7.1 5.4 5.4"/>',
 "refresh": '<path d="M20.4 12a8.4 8.4 0 1 1-2.5-6"/><path d="M20.4 4.2V10h-5.8"/>',
 "moon": '<path d="M20.2 13.4A8.4 8.4 0 1 1 10.6 3.8a6.6 6.6 0 0 0 9.6 9.6Z"/>',
 "tag": '<path d="M11.4 3.6H4.6a1 1 0 0 0-1 1v6.8a1 1 0 0 0 .3.7l8.2 8.2a1 1 0 0 0 1.4 0l6.8-6.8a1 1 0 0 0 0-1.4l-8.2-8.2a1 1 0 0 0-.7-.3Z"/><circle cx="8" cy="8" r="1.2"/>',
 "factory": '<path d="M3.6 20.4V10l5.6 3.4V10l5.6 3.4V6.6h5.6v13.8Z"/><path d="M3.6 20.4h16.8"/>',
 "cloud": '<path d="M17.6 18.6H7a4.4 4.4 0 0 1-.5-8.77 6 6 0 0 1 11.5 1.6 3.6 3.6 0 0 1-.4 7.17Z"/>',
 "scale": '<path d="M12 4v16"/><path d="M6 8h12"/><path d="M6 8 3.4 14h5.2Z"/><path d="M18 8l-2.6 6h5.2Z"/><path d="M8 20.4h8"/>',
 "mic": '<rect x="9" y="3.4" width="6" height="11" rx="3"/><path d="M5.6 11.6a6.4 6.4 0 0 0 12.8 0"/><path d="M12 18v2.6"/>',
 "seed": '<path d="M4.6 20.4c0-6.6 4.4-11 11-11 0 6.6-4.4 11-11 11Z"/><path d="M4.6 20.4c0-4.4 2.2-7.7 5.5-9.4"/>',
 "server": '<rect x="3.6" y="4.4" width="16.8" height="6" rx="1.4"/><rect x="3.6" y="13.6" width="16.8" height="6" rx="1.4"/><path d="M7 7.4h.01M7 16.6h.01"/>',
 "card": '<rect x="3" y="5.6" width="18" height="12.8" rx="2"/><path d="M3 10h18"/>',
 "phone": '<path d="M20.4 16.9v2.6a1.7 1.7 0 0 1-1.9 1.7 17 17 0 0 1-7.4-2.6 16.7 16.7 0 0 1-5.1-5.1A17 17 0 0 1 3.4 6a1.7 1.7 0 0 1 1.7-1.9h2.6a1.7 1.7 0 0 1 1.7 1.5c.1.8.3 1.7.6 2.5a1.7 1.7 0 0 1-.4 1.8l-1.1 1.1a13.6 13.6 0 0 0 5.1 5.1l1.1-1.1a1.7 1.7 0 0 1 1.8-.4c.8.3 1.6.5 2.5.6a1.7 1.7 0 0 1 1.4 1.7Z"/>',
 "rocket": '<path d="M8.6 15.4c-1.4 1.2-1.8 4.8-1.8 4.8s3.6-.4 4.8-1.8a2 2 0 1 0-3-3Z"/><path d="M12.6 13.4 10.6 11.4c1.6-4 4.6-6.6 9.4-6.8-.2 4.8-2.8 7.8-6.8 9.4Z"/><path d="M10.6 11.4H7.4l-2.2 3.2 3.4.8"/><path d="M12.6 13.4v3.2l3.2 2.2.8-3.4"/>',
 "book": '<path d="M4.4 4.6h5.2A2.4 2.4 0 0 1 12 7v12.4a2.2 2.2 0 0 0-2.4-1.6H4.4Z"/><path d="M19.6 4.6h-5.2A2.4 2.4 0 0 0 12 7v12.4a2.2 2.2 0 0 1 2.4-1.6h5.2Z"/>',
 "grad": '<path d="M2.6 8.6 12 4.4l9.4 4.2L12 12.8Z"/><path d="M6.4 10.6v4.8c0 1.8 2.5 3.2 5.6 3.2s5.6-1.4 5.6-3.2v-4.8"/>',
 "flag": '<path d="M5 20.4V4.4"/><path d="M5 5.2h11.6l-2 3.4 2 3.4H5"/>',
 "thumb": '<path d="M7.4 20.4V10.6l4-7a2 2 0 0 1 2.8 1.8v3.6h4.4a2 2 0 0 1 2 2.4l-1.4 6.6a2 2 0 0 1-2 1.4Z"/><path d="M7.4 10.6H4.6v9.8h2.8"/>',
 "info": '<circle cx="12" cy="12" r="8.4"/><path d="M12 16.2v-4.6M12 8.4h.01"/>',
}
sprite = ['<svg width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true">',
          '<!-- 图标全部内联，无 CDN、无字体、无外部图片；每个 24 视框、1.75 描边、跟随 currentColor -->']
for k, v in ICONS.items():
    sprite.append('<symbol id="i-%s" viewBox="0 0 24 24">%s</symbol>' % (k, v))
sprite.append('</svg>')
rep("<body>\n", "<body>\n" + "\n".join(sprite) + "\n", "注入 SVG 雪碧图")

# ============================================================
# 5. 底部 tab：五个改四个
# ============================================================
def tab(key, icon, label, badge=""):
    return ('            <div class="tab-item%s" data-tab="%s" onclick="switchTab(\'%s\')">\n'
            '                <span class="tab-icon"><svg class="ic"><use href="#i-%s"></use></svg></span>\n'
            '                <span class="tab-label">%s</span>%s\n'
            '            </div>\n') % (" active" if key == "home" else "", key, key, icon, label, badge)

NEW_TABS = ('        <div class="tab-bar" id="tabBar">\n'
            + tab("home", "home", "首页")
            + tab("company", "company", "管公司", '\n                <span class="tab-badge" id="riskBadge"></span>')
            + tab("opportunity", "target", "找机会")
            + tab("circle", "plaza", "小事广场")
            + "        </div>\n")
cut('        <div class="tab-bar" id="tabBar">', "    </div>\n\n    <script>", NEW_TABS, "底部四 tab")

# ============================================================
# 6. 首页：头像、管家卡、提醒卡、删两块、办事入口
# ============================================================
rep('<div class="home-avatar" onclick="switchTab(\'profile\')">👤</div>',
    '<div class="home-avatar" onclick="switchTab(\'profile\')"><svg class="ic ic-20"><use href="#i-user"></use></svg></div>',
    "首页头像图标")
repn('你好，<strong>创业者</strong> 👋', '你好，<strong>创业者</strong>', 3, "问候语去 emoji")
rep('你好，<strong>未来创业者</strong> 👋', '你好，<strong>未来创业者</strong>', "未来创业者问候语")
rep("""                            <div class="ce-avatar">
                                🧑‍💼
                                <span class="online-dot"></span>
                            </div>""",
    """                            <div class="ce-avatar">
                                <svg class="ic ic-22"><use href="#i-spark"></use></svg>
                                <span class="online-dot"></span>
                            </div>""", "管家头像图标")

rep("""                    <div class="alert-card alert-warning" onclick="openServiceDetail('行政日历')">
                        <span class="alert-icon">📅</span>
                        <div class="alert-text">下周三 社保缴费截止日 · 别忘了申报</div>
                        <span class="alert-close">✕</span>
                    </div>
                    <div class="alert-card alert-info" id="policyAlert" onclick="openServiceDetail('政策补贴')">
                        <span class="alert-icon">📋</span>
                        <div class="alert-text">政策库加载中</div>
                        <span class="alert-close">›</span>
                    </div>""",
    """                    <div class="alert-card alert-warning" onclick="openServiceDetail('行政日历')">
                        <span class="alert-icon"><svg class="ic ic-18"><use href="#i-calendar"></use></svg></span>
                        <div class="alert-text">下周三 社保缴费截止日 · 别忘了申报 <span class="demo-tag">演示数据</span></div>
                        <span class="alert-close"><svg class="ic ic-16"><use href="#i-close"></use></svg></span>
                    </div>
                    <div class="alert-card alert-info" id="policyAlert" onclick="openServiceDetail('政策补贴')">
                        <span class="alert-icon"><svg class="ic ic-18"><use href="#i-doc"></use></svg></span>
                        <div class="alert-text">政策库加载中</div>
                        <span class="alert-close"><svg class="ic ic-16"><use href="#i-chevron"></use></svg></span>
                    </div>""", "首页两张提醒卡")

# 删五大场景整块 + 九宫格换成办事入口
rep("""                    <div class="scenario-bar">
                        <div class="scenario-bar-title">五大场景覆盖</div>
                        <div class="scenario-tags">
                            <span class="scene-tag scene-policy">政策对接</span>
                            <span class="scene-tag scene-finance">融资对接</span>
                            <span class="scene-tag scene-scene">场景对接</span>
                            <span class="scene-tag scene-eco">生态活动</span>
                            <span class="scene-tag scene-industry">产业服务</span>
                        </div>
                    </div>

                    <div class="quick-grid">
                        <div class="quick-item" onclick="openServiceDetail('政策补贴')">
                            <span class="qi-icon">📋</span>
                            <span class="qi-label">政策补贴</span>
                        </div>
                        <div class="quick-item" onclick="openServiceDetail('开单诊断')">
                            <span class="qi-icon">🔍</span>
                            <span class="qi-label">开单诊断</span>
                        </div>
                        <div class="quick-item" onclick="openRiskPage()">
                            <span class="qi-icon">⚠️</span>
                            <span class="qi-label">风险一览</span>
                        </div>
                        <div class="quick-item" onclick="openServiceDetail('五险一金')">
                            <span class="qi-icon">🛡️</span>
                            <span class="qi-label">五险一金</span>
                        </div>
                    </div>
""",
    """                    <div class="task-head">
                        <h3>我要办的事</h3>
                        <span>按你的档案排序</span>
                    </div>
                    <div class="task-grid" id="taskGrid"></div>
""", "删五大场景、九宫格换办事入口")

# 删「为您推荐」与两条 banner
rep("""
                    <div class="section-header">
                        <h3>💡 为您推荐</h3>
                    </div>
                    <div class="feature-banner fb-park" style="margin:0 20px 12px;" onclick="openServiceDetail('园区服务')">
                        <span class="fb-icon">🏢</span>
                        <div class="fb-text">
                            <div class="fb-title">园区入驻诊断</div>
                            <div class="fb-sub">看看哪个园区适合你</div>
                        </div>
                        <span class="fb-arrow">→</span>
                    </div>
                    <div class="feature-banner fb-overseas" style="margin:0 20px 16px;" onclick="openServiceDetail('出海去')">
                        <span class="fb-icon">🌊</span>
                        <div class="fb-text">
                            <div class="fb-title">出海去</div>
                            <div class="fb-sub">海外同行动态 & 出海合规诊断</div>
                        </div>
                        <span class="fb-arrow">→</span>
                    </div>
""", "\n", "删为您推荐与两条 banner")

# 首页四个 section-header 去 emoji
for old, new in [("<h3>🔥 紧急待办</h3>", "<h3>紧急待办</h3>"),
                 ("<h3>⚠️ 风险提示</h3>", "<h3>风险提示</h3>"),
                 ("<h3>🎯 推荐机会</h3>", "<h3>推荐机会</h3>"),
                 ("<h3>📅 近期日程</h3>", "<h3>近期日程</h3>")]:
    rep(old, new, "首页标题 " + new)

# ============================================================
# 7. 服务页 → 管公司页（含风险页并入）
# ============================================================
def scard(name, icon, desc, onclick, badge_html):
    return ('                        <div class="service-card" onclick="%s">\n'
            '                            <span class="sc-icon"><svg class="ic ic-26"><use href="#i-%s"></use></svg></span>\n'
            '                            <span class="sc-name">%s</span>\n'
            '                            <span class="sc-desc">%s</span>\n'
            '                            %s\n'
            '                        </div>\n') % (onclick, icon, name, desc, badge_html)

LIB = '<span class="ev-badge ev-lib">库内数据</span>'
GEN = '<span class="ev-badge ev-none">通用流程</span>'
DEMO = '<span class="ev-badge ev-none">演示内容</span>'

COMPANY = """            <!-- 管公司 Screen（原「服务」+ 原「风险」并成一页） -->
            <div class="screen" id="screenCompany">
                <div class="service-header">
                    <h2>管公司</h2>
                    <p>经营事项与合规风险，都在这儿</p>
                </div>
                <div class="cm-seg">
                    <div class="cm-seg-i on" id="cmSegBiz" onclick="setCompanySection('biz')">经营事项</div>
                    <div class="cm-seg-i" id="cmSegRisk" onclick="setCompanySection('risk')">合规风险<span class="cm-seg-badge" id="cmRiskBadge"></span></div>
                </div>
                <div class="service-scroll" id="cmBizPane">
                    <div class="page-section-title">有命题方库内数据支撑</div>
                    <div class="service-grid">
""" + scard("政策补贴", "doc", "175 条政策库逐条比对", "openServiceDetail('政策补贴')", LIB) \
    + scard("金融服务", "bank", "8 家机构 67 个产品过筛", "openServiceDetail('金融服务')", LIB) \
    + scard("融资机会", "coin", "股权与投行类产品匹配", "openServiceDetail('融资机会')", LIB) \
    + scard("知识产权", "award", "流程 + 库内资助与质押贴息", "openTaskPage('知产')", LIB) \
    + scard("找场地", "pin", "北辰四大园区 + 载体政策", "openTaskPage('场地')", LIB) \
    + scard("招人用工", "users", "用工合规 + 人才支持政策", "openTaskPage('招人')", LIB) \
    + """                    </div>
                    <div class="page-section-title">通用办事流程 · 命题方未提供数据</div>
                    <div class="service-grid">
""" + scard("开公司", "biz", "核名到开户五步清单", "openTaskPage('开公司')", GEN) \
    + scard("交社保", "shield", "开户、缴费、公积金", "openTaskPage('社保')", GEN) \
    + scard("报税", "receipt", "登记、票种、按期申报", "openTaskPage('报税')", GEN) \
    + scard("行政日历", "calendar", "重要日期与待办管理", "openServiceDetail('行政日历')", DEMO) \
    + """                    </div>
                    <div class="more-toggle" id="moreToggle" onclick="toggleMoreServices()">
                        更多服务<span class="mt-sub">演示内容，无数据支撑</span>
                        <svg class="ic ic-18"><use href="#i-chevron"></use></svg>
                    </div>
                    <div class="service-grid" id="moreServices" style="display:none;">
""" + scard("开单诊断", "check", "合规手续全面检查", "openServiceDetail('开单诊断')", DEMO) \
    + scard("云服务规划", "cloud", "服务器·域名·算力·收款", "openServiceDetail('云服务规划')", DEMO) \
    + scard("找顾问", "scale", "注册·财会·法务·知产", "openServiceDetail('找顾问')", DEMO) \
    + scard("五险一金", "shield", "缴费提醒·补贴·提取", "openServiceDetail('五险一金')", DEMO) \
    + scard("出海去", "globe", "海外动态与合规诊断", "openServiceDetail('出海去')", DEMO) \
    + """                    </div>
                    <div class="ev-panel">
                        <div class="ev-panel-t"><svg class="ic ic-16"><use href="#i-file"></use></svg>这页的数据边界</div>
                        <div class="ev-line"><span class="ev-key">原文照抄</span><span class="ev-val">政策补贴、金融服务、融资机会、知识产权、找场地、招人，条目与字段全部来自命题方两个库</span></div>
                        <div class="ev-line k-none"><span class="ev-key">通用口径</span><span class="ev-val">开公司、交社保、报税只讲办事顺序，不写时限、费用、截止日，命题方数据库未覆盖这三类</span></div>
                        <div class="ev-line k-none"><span class="ev-key">演示内容</span><span class="ev-val">更多服务里的五项与行政日历的日期是演示数据，不作为办理依据</span></div>
                    </div>
                </div>
                <div class="service-scroll" id="riskScroll" style="display:none;"></div>
            </div>

"""
cut("            <!-- Service Screen -->", "            <!-- Circle Screen -->", COMPANY, "服务页改管公司页")

# 机会 tab 改名找机会
rep("""            <!-- 机会 Tab -->
            <div class="screen" id="screenOpportunity">
                <div class="service-header">
                    <h2>机会</h2>""",
    """            <!-- 找机会 Tab -->
            <div class="screen" id="screenOpportunity">
                <div class="service-header">
                    <h2>找机会</h2>""", "机会改名找机会")

# 风险 tab 整屏删掉（内容已并进管公司）
cut("""            <!-- 风险 Tab -->
            <div class="screen" id="screenRisk">""", "            <!-- Chat Overlay -->", "", "删风险独立屏")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第一趟完成，文件已写回")

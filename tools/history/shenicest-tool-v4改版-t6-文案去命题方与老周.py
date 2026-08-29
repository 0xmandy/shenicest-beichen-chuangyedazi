# -*- coding: utf-8 -*-
"""第六趟：文案与信息层重写。
1 管家改名老周并恢复头像 2 命题方措辞全部去掉 3 库内条数标签不展示
4 数据边界与口径横幅全部删除 5 经营事项按政务大厅顺序重排
6 办事流程换成检索到的北京官方口径"""
import io, re, sys

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
    global src
    n = src.count(old)
    if n != times:
        sys.exit("锚点[%s]命中 %d 次，应为 %d 次，退出" % (label, n, times))
    src = src.replace(old, new)
    print("  ok  %s（%d）" % (label, times))

def cut(start, end, new, label):
    global src
    if src.count(start) != 1 or src.count(end) != 1:
        sys.exit("区间锚点[%s]不唯一，退出" % label)
    i = src.index(start); j = src.index(end)
    if j <= i: sys.exit("区间锚点[%s]顺序不对" % label)
    src = src[:i] + new + src[j:]
    print("  ok  %s" % label)

def drop_lines(marker, expect, label):
    """整行删掉含 marker 的行"""
    global src
    lines = src.split("\n")
    hit = [l for l in lines if marker in l]
    if len(hit) != expect:
        sys.exit("行锚点[%s]命中 %d 行，应为 %d 行，退出" % (label, len(hit), expect))
    src = "\n".join([l for l in lines if marker not in l])
    print("  ok  %s（删 %d 行）" % (label, expect))

# ============================================================
# 1 管家老周
# ============================================================
rep("""                            <div class="ce-avatar">
                                <svg class="ic ic-22"><use href="#i-spark"></use></svg>
                                <span class="online-dot"></span>
                            </div>
                            <div class="ce-info">
                                <div class="ce-name">
                                    <span class="name">智能管家</span>
                                </div>
                                <div class="ce-status">
                                    <span class="pulse"></span>
                                    正在跟进你的合规风险
                                </div>
                            </div>""",
    """                            <div class="ce-avatar">
                                \U0001F9D1‍\U0001F4BC
                                <span class="online-dot"></span>
                            </div>
                            <div class="ce-info">
                                <div class="ce-name">
                                    <span class="name">老周</span>
                                    <span class="ce-role">创业管家</span>
                                </div>
                                <div class="ce-status">
                                    <span class="pulse"></span>
                                    正在跟进你的专精特新申报
                                </div>
                            </div>""", "首页管家卡改老周")

rep("""        .ce-name {""",
    """        .ce-role {
            font-size: 11px; font-weight: 500; color: var(--n500);
            background: var(--n100); border-radius: var(--r-xs); padding: 1px 7px;
        }
        .ce-name {""", "管家身份标样式")

rep("""                    <span class="ch-title"><svg class="ic ic-18"><use href="#i-spark"></use></svg> 智能管家</span>""",
    """                    <span class="ch-title">\U0001F9D1‍\U0001F4BC 老周 · 创业管家</span>""", "对话页标题改老周")

rep("""                    <div class="msg msg-ai">我是你的创业管家。<br/>命题方给的 175 条政策和 67 个金融产品已经全接进我的库里。问政策我只答库里有的，额度利率只吐原表的字，答不上就说答不上。</div>""",
    """                    <div class="msg msg-ai">我是老周，你的创业管家。<br/>政策、补贴、融资、办事流程都可以问我。我拿你的档案去比对，能办的、缺什么、去哪办，一条条说给你听。</div>""",
    "对话开场白")

rep("""                msg = '我已经把命题方的 ' + (POLICY_DOCS.length + POLICY_READS.length) + ' 条政策全接进来了。你告诉我做哪个行业，我拿你的档案逐条比对。';""",
    """                msg = '政策和补贴我都盯着。你告诉我做哪个行业，我拿你的档案逐条比对，能申报的挑出来给你。';""",
    "管家开场白无行业分支")

rep("""            bubble.innerHTML = msg + '条件、额度、截止日我不猜，点进去看原文。';""",
    """            bubble.innerHTML = msg + '点进去能看到官方原文。';""", "管家气泡结尾")

# ============================================================
# 2 冷启动页文案
# ============================================================
rep("""                        <div class="ob-welcome-icon"><svg class="ic ic-40"><use href="#i-spark"></use></svg></div>
                        <div class="ob-welcome-title">创业搭子</div>
                        <div class="ob-welcome-sub">北辰产业云社区的 AI 创业管家<br/>政策、金融、待办、风险，我替你盯</div>
                        <div class="ob-tags">
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-doc"></use></svg> 175 条政策库</span>
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-bank"></use></svg> 67 个金融产品</span>
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-chat"></use></svg> 答不上就说答不上</span>
                        </div>""",
    """                        <div class="ob-welcome-icon">\U0001F9D1‍\U0001F4BC</div>
                        <div class="ob-welcome-title">创业搭子</div>
                        <div class="ob-welcome-sub">我是老周，你的创业管家<br/>政策、找钱、办事、风险，我替你盯</div>
                        <div class="ob-tags">
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-doc"></use></svg> 帮你领补贴</span>
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-bank"></use></svg> 帮你找钱</span>
                            <span class="ob-tag"><svg class="ic ic-16"><use href="#i-check"></use></svg> 帮你跑手续</span>
                        </div>""", "冷启动欢迎页")

# ============================================================
# 3 数据边界、口径横幅、来源行全部删除
# ============================================================
drop_lines('body += `<div class="ev-panel">', 2, "政策页与金融页的数据边界")
drop_lines('html += `<div class="ev-panel">', 1, "找机会页的数据边界")
drop_lines('<div class="pol-src">来源：', 2, "政策卡与贴息卡的来源行")
drop_lines('<div class="pol-dbline">', 2, "政策页与金融页顶部的库说明行")

# 政策详情弹层：去掉「需要你自己核的」与「这条数据从哪来」，只留原文入口
rep("""                <div class="pd-block">
                    <div class="pd-h">需要你自己核的</div>
                    <div class="pd-line pd-warn">申报条件：原库未结构化，以原文为准</div>
                    <div class="pd-line pd-warn">补贴额度：原库未结构化，以原文为准</div>
                    <div class="pd-line pd-warn">截止日期：原库未结构化，以原文为准</div>
                </div>
                <div class="pd-block">
                    <div class="pd-h">这条数据从哪来</div>
                    <div class="pd-line">${p.kind === 'doc' ? POLICY_SOURCE.docs : POLICY_SOURCE.reads}</div>
                    <div class="pd-line">库内编号 ${p.id}${p.file ? ' · 原文件 ' + p.file : ''}${p.date ? ' · 发布 ' + p.date : ''}</div>
                </div>""",
    """                <div class="pd-block">
                    <div class="pd-h">申报条件与额度</div>
                    <div class="pd-line">具体条件、支持额度和申报截止时间，以下面的官方原文为准。拿不准的可以问老周，或者找园区企服中心确认。</div>
                </div>""", "政策详情去溯源块")

rep("""<div class="pd-line pd-warn">这份是全文导入的原文件，库里没有配套的公开链接，需要在园区企服中心调原件。</div>""",
    """<div class="pd-line pd-warn">这份没有配套的公开链接，可以到园区企服中心调原件。</div>""", "政策原文兜底话术")

# 金融详情弹层：去掉「这条数据从哪来」
rep("""                <div class="pd-block"><div class="pd-h">这条数据从哪来</div>
                    <div class="pd-line">${FIN_SOURCE}</div>
                    <div class="pd-line">库内编号 ${p.id}${p.amountKnown ? '' : ' · 额度原表写「根据企业实际情况不定」'}${p.rateKnown ? '' : ' · 利率原表写「根据企业实际情况不定」'}</div></div>""",
    "", "金融详情去溯源块")

# 管家问答的两段脚注
drop_lines('<div class="ans-foot">以上条目名称与链接原样来自命题方政策库', 1, "问答政策脚注")
drop_lines('<div class="ans-foot">四要素原样来自命题方金融库', 1, "问答金融脚注")

# 口径横幅 helper 与它的五处调用
rep("""        // 口径横幅：通用流程 / 演示内容 / 数据来源，闭合标签只在这一处写
        function evGeneric(title, desc) {
            return '<div class="ev-generic">' + ic('info', 18)
                 + '<div><div class="ev-generic-t">' + title + '</div>'
                 + '<div class="ev-generic-d">' + desc + '</div></div></div>';
        }

""", "", "删口径横幅 helper")
rep("""            if (data.demo) {
                html += evGeneric('演示内容，无命题方数据支撑',
                    '这一页命题方数据库没有覆盖，内容用于演示交互，不作为办理依据。有真数据的是政策补贴、金融服务、融资机会，以及办事入口里的知识产权、找场地、招人。');
            }
""", "", "删服务页演示横幅")
rep("""            document.getElementById('pageScroll').innerHTML = evGeneric('日程为演示数据',
                '这里的日期用于演示小事引擎的写入与勾销，不来自命题方政策库或金融库，不作为申报或缴费依据。') + `
                <div class="cal-card">""",
    """            document.getElementById('pageScroll').innerHTML = `
                <div class="cal-card">""", "删行政日历演示横幅")

# 风险页脚注改成对用户有用的一句
rep("""            html += '<div class="foot-note">风险评分是演示用的规则打分，说明的是倾向，不构成合规结论。判定不了的条目一律显式标「需人工核」，管家不替你下判断。</div>';""",
    """            html += '<div class="foot-note">这些提示按你的档案生成，说明的是倾向，不是合规结论。拿不准的事项建议找园区企服中心或专业顾问确认。</div>';""",
    "风险页脚注")

# 零散措辞
repn("命题方政策库 · ", "相关政策 · ", 1, "办事页政策小节标题")
repn("命题方金融库 · ", "相关金融产品 · ", 1, "办事页金融小节标题")
rep("html += '<div class=\"page-section-title\">政策机会 · 来自命题方政策库</div>';",
    "html += '<div class=\"page-section-title\">政策机会</div>';", "找机会政策标题")
rep("html += '<div class=\"page-section-title\">金融机会 · 来自命题方金融库</div>';",
    "html += '<div class=\"page-section-title\">金融机会</div>';", "找机会金融标题")
rep("""    <!-- 本文件属于 shenicest 黑客松北辰商管命题。
         政策数据来源：命题方《政策智能体数据库.xlsx》，原文库 86 份 + 解读库 89 条，标题与链接原样保留。 -->""",
    """    <!-- 本文件属于「创业搭子」原型。
         政策数据 175 条（原文库 86 份 + 解读库 89 条）与金融数据 76 条由脚本结构化导入，标题与链接原样保留。
         办事流程取自北京市官方口径：e 窗通企业开办、电子税务局票种核定、社保网上服务平台、工信部 App 与小程序备案、网信办生成式 AI 备案。 -->""",
    "文件头注释")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第六趟前半完成")

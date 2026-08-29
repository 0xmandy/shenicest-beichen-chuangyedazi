# -*- coding: utf-8 -*-
"""第八趟（v5）：命中改匹配、首页悬浮入口改老周对话、办事流程补成第三个知识源、老周不用「盯」。

属于 shenicest 黑客松北辰商管命题的「创业搭子」原型。
改的是同目录 shenicest-北辰-创业搭子-原型-2026-08-27.html。

三件事：
  1 「命中」统一改成匹配的说法，一条理由里不再出现两次。逐条前缀去掉，整块加一行「匹配理由」小标题。
  2 首页右下角悬浮按钮改成老周的对话入口（小事广场仍是记一件小事）；
    老周的问答从两个知识源（政策库、金融库）补成三个，新增办事流程库。
  3 老周负责的事改成提醒口吻，风险文案里的「被风控盯上」不动。

数据纪律不变：
  - 政策与金融的额度、期限、利率只来自两个库的原文，原表写「根据企业实际情况不定」的显示
    「以机构核定为准」，本脚本一个字没碰。
  - 办事流程库直接复用页面里已有的 TASK_PAGES 十三页，只做检索与摘录，不新增任何数字。
    这十三页的北京市官方口径与出处见 shenicest-tool-v4改版-t7-北京办事流程.py 头部注释
    （e 窗通一天办结、公积金第二个工作日完成开户、社会保险就业劳动用工统一登记、
    工信部信管〔2023〕105 号二十个工作日审核、《生成式人工智能服务管理暂行办法》属地备案与公示）。

一次性的单向迁移记录，跑过之后锚点已不存在，重跑会报错。
"""
import io, sys

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-2026-08-27.html"
src = io.open(PATH, encoding="utf-8").read()


def rep(old, new, label, times=1):
    global src
    n = src.count(old)
    if n != times:
        sys.exit("锚点[%s]命中 %d 次，应为 %d 次，退出" % (label, n, times))
    src = src.replace(old, new)
    print("  ok  %s" % label)


# ============================================================
# 1 「命中」改「匹配」
# ============================================================
print("[1] 命中改匹配")

rep("// 打分规则全部显式写出来，界面上逐条回显命中理由。",
    "// 打分规则全部显式写出来，界面上逐条回显匹配理由。", "注释")

# A 类：打分理由的前缀，政策 9 条
A = [
    ("'地域命中：朝阳区，北辰四大园区所在辖区'", "'地域：朝阳区，北辰四大园区所在辖区'"),
    ("'地域命中：' + p.level + '，你所在城市可申报'", "'地域：' + p.level + '，你所在城市可申报'"),
    ("'行业主标签命中：' + state.industry", "'行业：' + state.industry"),
    ("'相关标签命中：' + hitTags.join('、')", "'相关方向：' + hitTags.join('、')"),
    ("'主体命中：面向中小微企业'", "'主体：面向中小微企业'"),
    ("'阶段命中：还没注册主体，先看人才与创业支持类'", "'阶段：还没注册主体，先看人才与创业支持类'"),
    ("'阶段命中：已有主体，可对接融资类支持'", "'阶段：已有主体，可对接融资类支持'"),
    ("'身份命中：在校生，青年人才类条目'", "'身份：在校生，青年人才类条目'"),
    ("'出海命中：你勾了出海业务'", "'出海：你勾了出海业务'"),
    # A 类：金融 5 条
    ("'行业命中：你做数据要素，这条是数据资产类产品'", "'行业：你做数据要素，这条是数据资产类产品'"),
    ("'行业命中：科技型企业专项'", "'行业：科技型企业专项'"),
    ("'条件命中：' + c", "'条件：' + c"),
    ("'阶段命中：还没有企业主体，个人金融类先能用上'", "'阶段：还没有企业主体，个人金融类先能用上'"),
    ("'阶段命中：原表标为初创期融资产品'", "'阶段：原表标为初创期融资产品'"),
]
for i, (o, n) in enumerate(A):
    rep(o, n, "打分理由 %d/%d" % (i + 1, len(A)))

# B 类：卡片上的重复前缀。逐条前缀去掉，整块加一行小标题
rep("""${showReason && p._reasons && p._reasons.length ? `<div class="pol-reason">${p._reasons.slice(0, 3).map(r => `<div class="pol-reason-line">命中 · ${r}</div>`).join('')}</div>` : ''}""",
    """${showReason && p._reasons && p._reasons.length ? `<div class="pol-reason"><div class="pol-reason-h">匹配理由</div>${p._reasons.slice(0, 3).map(r => `<div class="pol-reason-line">${r}</div>`).join('')}</div>` : ''}""",
    "政策卡去重复前缀")

rep("""${p._reasons && p._reasons.length ? `<div class="pol-reason">${p._reasons.slice(0, 3).map(r => `<div class="pol-reason-line">命中 · ${r}</div>`).join('')}</div>` : ''}""",
    """${p._reasons && p._reasons.length ? `<div class="pol-reason"><div class="pol-reason-h">匹配理由</div>${p._reasons.slice(0, 3).map(r => `<div class="pol-reason-line">${r}</div>`).join('')}</div>` : ''}""",
    "金融卡去重复前缀")

rep("        .pol-reason-line { font-size:11px; color:var(--text-secondary); line-height:1.7; }",
    "        .pol-reason-h { font-size:10px; font-weight:600; color:var(--text-light); margin-bottom:3px; }\n"
    "        .pol-reason-line { font-size:11px; color:var(--text-secondary); line-height:1.7; }",
    "匹配理由小标题样式")

# C 类：兜底文案
rep("当前档案没有命中条件，这条是全库检索结果。",
    "当前档案没有匹配上，这条是全库检索结果。", "政策详情兜底")
rep("当前条件没有命中，这条是库内浏览结果。",
    "当前条件没有匹配上，这条是库内浏览结果。", "金融详情兜底")

if "命中" in src:
    sys.exit("还有「命中」残留：%s" % [l.strip()[:80] for l in src.split("\n") if "命中" in l][:5])
print("  ok  全文「命中」归零")


# ============================================================
# 2 首页悬浮入口改老周对话 + 办事流程补成第三个知识源
# ============================================================
print("[2] 首页对话入口与第三个知识源")

# 2a 悬浮按钮：一颗两用，首页克制些，别抢「猜您需要」的视觉重心
rep("        .fab { box-shadow: 0 6px 20px rgba(229,83,43,.38); }",
    "        .fab { box-shadow: 0 6px 20px rgba(229,83,43,.38); }\n"
    "        /* 首页那颗是老周的对话入口，比小事广场的加号克制：浅底描边，不抢「猜您需要」的重心 */\n"
    "        .fab.fab-chat { width:48px; height:48px; background:var(--card); color:var(--brand); border:var(--hair); box-shadow:0 4px 14px rgba(38,35,31,.12); }",
    "首页悬浮按钮样式")

rep("""        <div class="fab" id="fabAdd" onclick="openSmallThing()">+</div>""",
    """        <div class="fab" id="fabAdd" onclick="fabTap()">+</div>""",
    "悬浮按钮改分发")

rep("""            const fab = document.getElementById('fabAdd');
            if (fab) fab.style.display = tab === 'circle' ? 'flex' : 'none';""",
    """            syncFab(tab);""",
    "switchTab 里换成 syncFab")

rep("""        // ===== Chat Logic =====
        function openChat() {""",
    """        // 悬浮按钮一颗两用：首页是老周的对话入口，小事广场是记一件小事，其余两个 tab 不显示
        function syncFab(tab) {
            const fab = document.getElementById('fabAdd');
            if (!fab) return;
            if (tab === 'home') {
                fab.classList.add('fab-chat');
                fab.innerHTML = ic('chat', 22);
            } else if (tab === 'circle') {
                fab.classList.remove('fab-chat');
                fab.textContent = '+';
            }
            fab.style.display = (tab === 'home' || tab === 'circle') ? 'flex' : 'none';
        }

        function fabTap() {
            if (state.currentTab === 'home') { openChat(); return; }
            openSmallThing();
        }

        // ===== Chat Logic =====
        function openChat() {""",
    "syncFab 与 fabTap")

# 2b 办事流程库：第三个知识源
rep("""        // ===== 小事引擎（从 coze 有数_demo 搬过来的前后逻辑）=====""",
    """        // ===== 第三个知识源：办事流程库 =====
        // 数据就是下面 TASK_PAGES 那十三页，北京市官方口径。这里只做检索与摘录，不新增任何数字。
        // 十三页每条口径的出处见 shenicest-tool-v4改版-t7-北京办事流程.py 头部注释。
        // 关键词都挑得比较具体：不收「申报」「园区」「开户」这种谁都能沾的词，
        // 否则「我能申报哪些政策」会被报税页截走、「转接园区人工」会被找场地页截走。
        const TASK_KEYWORDS = {
            '开公司': ['开公司', '注册公司', '公司注册', '注册主体', '注册流程', '怎么注册', '注册', '营业执照', '执照', '核名', '名称自主申报', '刻章', '公章', '窗通', '开办企业', '对公户', '对公账户', '基本存款账户'],
            '社保': ['社保', '公积金', '参保', '增员', '减员', '五险一金', '社会保险', '缴费基数'],
            '报税': ['报税', '税务', '税种', '税费种', '纳税申报', '零申报', '汇算', '清缴', '三方协议'],
            '发票': ['发票', '开票', '票种', 'ukey', '税控'],
            '招人': ['招人', '用工', '劳动合同', '员工', '入职', '考勤', '工资台账', '规章制度'],
            '知产': ['专利', '商标', '商标注册', '软著', '软件著作权', '知识产权'],
            '场地': ['场地', '租金', '入驻', '办公室', '工位', '找地方'],
            '出海': ['出海', '跨境', '海外', '境外'],
            'app': ['app', '上架', '应用商店', '应用市场', 'icp备案'],
            '小程序': ['小程序'],
            'aigc': ['aigc', '大模型', '生成式', '算法备案', '模型备案'],
            '自媒体': ['自媒体', '商单', '短视频', '带货', '公众号', '视频号'],
            '合同': ['合同', '签约', '用印', '盖章', '违约'],
        };

        // 沾钱的问法让金融库先答。「知识产权质押有没有贴息」问的是钱，不是办证顺序。
        const MONEY_FIRST = /贷款|贷|授信|额度|利率|抵押|质押|贴息|融资|担保|保理|贴现|股权投资/;

        function taskQuery(text) {
            const t = String(text).toLowerCase();
            let best = null;
            Object.keys(TASK_KEYWORDS).forEach(function (k) {
                let sc = 0;
                TASK_KEYWORDS[k].forEach(function (w) { if (t.indexOf(w) >= 0) sc += w.length; });
                if (sc > 0 && (!best || sc > best.sc)) best = { key: k, sc: sc };
            });
            return best;
        }

        // 回答卡只给一句引子、前三步、在哪办，剩下的推到完整流程页，聊天窗里塞不下五步
        function taskAnswerHTML(key) {
            const d = TASK_PAGES[key];
            if (!d) return '';
            let h = `<div class="ans-lead">${d.lead}</div>`;
            const steps = (d.steps || []).slice(0, 3);
            if (steps.length) {
                h += '<div class="ans-steps">' + steps.map((s, i) => `
                    <div class="ans-step">
                        <span class="ans-no">${i + 1}</span>
                        <div><div class="ans-st">${s.t}</div><div class="ans-sd">${s.d}</div></div>
                    </div>`).join('') + '</div>';
            }
            if (d.where) h += `<div class="ans-where">在哪办：${d.where}</div>`;
            h += `<div class="ans-btn" onclick="openTaskPage('${key}')">看完整流程</div>`;
            return h;
        }

        // ===== 小事引擎（从 coze 有数_demo 搬过来的前后逻辑）=====""",
    "办事流程知识源")

rep("""        .ans-none { font-size:13px; line-height:1.8; }""",
    """        .ans-none { font-size:13px; line-height:1.8; }
        /* 管家问答里的办事流程卡 */
        .ans-steps { margin-top:9px; }
        .ans-step { display:flex; gap:8px; align-items:flex-start; margin-bottom:9px; }
        .ans-no { flex:0 0 auto; width:17px; height:17px; border-radius:50%; background:var(--primary-light); color:var(--primary-dark); font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center; margin-top:2px; }
        .ans-st { font-size:12px; font-weight:600; line-height:1.5; }
        .ans-sd { font-size:11px; color:var(--text-secondary); line-height:1.7; margin-top:2px; }
        .ans-where { font-size:11px; color:var(--text-secondary); line-height:1.7; background:var(--bg); border-radius:var(--radius-sm); padding:9px 10px; }
        .ans-btn { margin-top:9px; text-align:center; font-size:12px; font-weight:600; color:var(--primary-dark); background:var(--primary-light); border-radius:var(--radius-sm); padding:10px; }""",
    "办事流程卡样式")

# 2c 问答分流：办事流程 > 金融 > 政策
rep("""        // 问答分流：沾政策的走政策库检索，其余走固定话术。
        // 政策类回答只允许出现库里有的名称、日期、链接，检索不到就明说检索不到。
        function respond(text) {
            setTimeout(function () {
                if (isFinanceQuestion(text)) {""",
    """        // 问答分流：三个知识源，办事流程 > 金融 > 政策，其余走固定话术。
        // 办事流程排最前是因为「社保怎么开户」这类问题以前会被政策库的关键词先截走，答非所问。
        // 沾了贷款、质押、贴息的问法反过来让金融库先答。
        // 政策与金融的回答只允许出现库里有的名称、日期、额度、利率、链接，检索不到就明说检索不到。
        function respond(text) {
            setTimeout(function () {
                const tk = taskQuery(text);
                if (tk && !MONEY_FIRST.test(text)) {
                    addRichMessage(taskAnswerHTML(tk.key));
                    return;
                }
                if (isFinanceQuestion(text)) {""",
    "问答分流补第三个源")

rep("""                addMessage('这个我这边没有对应的数据源，答不了。政策、申报、补贴这类我能查库，其余的可以转园区人工。', 'ai');""",
    """                addMessage('这个我暂时答不上来。政策、补贴、融资、开公司报税这些我熟，别的可以转园区企服中心的人工。', 'ai');""",
    "兜底改老周口吻")

# 2d 快捷问按钮混进办事流程类
rep("""                        <button class="mq-btn" onclick="sendQuick('我能申报哪些政策')">我能申报什么</button>
                        <button class="mq-btn" onclick="sendQuick('专精特新怎么认定')">专精特新</button>
                        <button class="mq-btn" onclick="sendQuick('智能机器人有什么支持政策')">机器人政策</button>
                        <button class="mq-btn" onclick="sendQuick('数据要素相关政策')">数据要素</button>
                        <button class="mq-btn" onclick="sendQuick('数据资产能不能质押贷款')">数据资产质押</button>
                        <button class="mq-btn" onclick="sendQuick('知识产权质押有没有贴息')">知产质押贴息</button>
                        <button class="mq-btn" onclick="sendQuick('帮我记录一个待办')">记录待办</button>
                        <button class="mq-btn" onclick="sendQuick('转接园区人工')">园区人工</button>""",
    """                        <button class="mq-btn" onclick="sendQuick('我能申报哪些政策')">我能申报什么</button>
                        <button class="mq-btn" onclick="sendQuick('专精特新怎么认定')">专精特新</button>
                        <button class="mq-btn" onclick="sendQuick('数据要素相关政策')">数据要素</button>
                        <button class="mq-btn" onclick="sendQuick('数据资产能不能质押贷款')">数据资产质押</button>
                        <button class="mq-btn" onclick="sendQuick('知识产权质押有没有贴息')">知产质押贴息</button>
                        <button class="mq-btn" onclick="sendQuick('开公司怎么办')">开公司</button>
                        <button class="mq-btn" onclick="sendQuick('社保怎么开户')">社保怎么开户</button>
                        <button class="mq-btn" onclick="sendQuick('发票怎么申领')">发票怎么申领</button>
                        <button class="mq-btn" onclick="sendQuick('AIGC 要备案吗')">AIGC 要备案吗</button>
                        <button class="mq-btn" onclick="sendQuick('转接园区人工')">园区人工</button>""",
    "快捷问补办事流程类")

rep("""我是老周，你的创业管家。<br/>政策、补贴、融资、办事流程都可以问我。我拿你的档案去比对，能办的、缺什么、去哪办，一条条说给你听。""",
    """我是老周，你的创业管家。<br/>政策、补贴、融资、办事流程都可以问我。我拿你的档案去比对，能办的、缺什么、去哪办，一条条说给你听。""",
    "开场白校验（不改，确认已提到办事流程）")


# ============================================================
# 3 老周不用「盯」，改提醒口吻。风险文案里的「被风控盯上」不动
# ============================================================
print("[3] 老周改提醒口吻")

rep("政策、找钱、办事、风险，我替你盯",
    "政策、找钱、办事、风险，该动手了我提醒你", "冷启动欢迎页副标题")

rep("""你的<strong class="highlight">社保缴费</strong>下周三截止，我帮你盯好了。政策、合规、待办都可以问我~""",
    """你的<strong class="highlight">社保缴费</strong>下周三截止，先跟你说一声。政策、合规、待办都可以问我~""",
    "首页管家气泡默认文案")

rep("msg = '政策和补贴我都盯着。你告诉我做哪个行业",
    "msg = '政策和补贴有新的我就提醒你。你告诉我做哪个行业", "管家开场白无行业分支")

left = [l.strip()[:70] for l in src.split("\n") if "盯" in l]
if len(left) != 1 or "风控盯上" not in left[0]:
    sys.exit("「盯」剩下的不是预期的那一处：%s" % left)
print("  ok  「盯」只剩风险文案里的「被风控盯上」，按要求保留")


# ============================================================
# 收尾断言
# ============================================================
import re
# 老周的 🧑‍💼 是全文唯一允许的 emoji，先摘掉它再看还剩什么
rest = src.replace("\U0001F9D1‍\U0001F4BC", "")
found = sorted(set(re.findall("[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", rest)))
if found:
    sys.exit("出现了新的 emoji：%s" % found)
print("  ok  emoji 只剩老周的 🧑‍💼")

for bad in ["这页的数据边界", "通用流程口径", "非政策原文"]:
    if bad in src:
        sys.exit("界面上出现了元描述「%s」" % bad)
print("  ok  无元描述残留")

for bad in ["http://cdn", "https://cdn", "<link", "@import", "<img"]:
    if bad in src:
        sys.exit("引入了外部依赖：%s" % bad)
print("  ok  单文件零外部依赖")

io.open(PATH, "w", encoding="utf-8").write(src)
print("写回 %s（%.0f KB）" % (PATH, len(src.encode("utf-8")) / 1024))

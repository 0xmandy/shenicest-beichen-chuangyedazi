# -*- coding: utf-8 -*-
"""第二趟：JS 层。tab 路由、办事入口、办事详情页、证据组件落地、emoji 全清。"""
import io, sys, re

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
    print("  ok  %s（%d 处）" % (label, times))

def cut(start, end, new, label):
    global src
    if src.count(start) != 1 or src.count(end) != 1:
        sys.exit("区间锚点[%s]不唯一，退出" % label)
    i = src.index(start); j = src.index(end)
    if j <= i: sys.exit("区间锚点[%s]顺序不对" % label)
    src = src[:i] + new + src[j:]
    print("  ok  %s" % label)

def svg(name, size=18):
    return '<svg class="ic ic-%d"><use href="#i-%s"></use></svg>' % (size, name)

# ============================================================
# A. 旧 pol-guard / pol-empty 样式换成证据面板与空状态
# ============================================================
rep("""        .pol-empty { margin:0 20px 12px; font-size:12px; color:var(--text-secondary); background:var(--card); border-radius:var(--radius-sm); padding:14px; line-height:1.7; }""",
    """        .pol-empty { margin:0 20px 12px; font-size:12px; color:var(--n500); background:var(--n0); border:1px dashed var(--n300); border-radius:var(--r-sm); padding:20px 16px; line-height:1.8; text-align:center; }""",
    "空状态样式")
rep("""        .pol-guard { margin:14px 20px 20px; background:var(--card); border-radius:var(--radius); padding:13px 14px; box-shadow:var(--shadow); border-left:3px solid var(--primary); }
        .pol-guard-t { font-size:13px; font-weight:600; margin-bottom:7px; color:var(--text); }
        .pol-guard-l { font-size:11px; color:var(--text-secondary); line-height:1.8; }
""", "", "删旧数据边界样式")

# 三处「这页的数据边界」换成证据面板：带前缀标签，不再是灰色小字
def ev_panel(rows):
    out = ['<div class="ev-panel">',
           '<div class="ev-panel-t">' + svg("file", 16) + '这页的数据边界</div>']
    for key, val, none in rows:
        out.append('<div class="ev-line%s"><span class="ev-key">%s</span><span class="ev-val">%s</span></div>' % (" k-none" if none else "", key, val))
    out.append('</div>')
    return "".join(out)

rep("""body += `<div class="pol-guard">
                    <div class="pol-guard-t">这页的数据边界</div>
                    <div class="pol-guard-l">政策名称、发布日期、原文链接：原样来自命题方政策库，一个字没改</div>
                    <div class="pol-guard-l">层级、主题标签、事项类型：从政策标题派生，用于匹配</div>
                    <div class="pol-guard-l">申报条件、补贴额度、截止日期：原库未结构化，管家不生成，点进去看原文</div>
                </div>`;""",
    "body += `" + ev_panel([
        ("原文照抄", "政策名称、发布日期、原文链接，原样来自命题方政策库，一个字没改", False),
        ("规则派生", "层级、主题标签、事项类型，从政策标题派生，只用于匹配排序", False),
        ("不生成", "申报条件、补贴额度、截止日期，原库未结构化，管家不生成，点进去看原文", True),
    ]) + "`;", "政策页数据边界")

rep("""body += `<div class="pol-guard">
                    <div class="pol-guard-t">这页的数据边界</div>
                    <div class="pol-guard-l">机构、产品名、适用门槛、核心特点、额度、期限、利率：原样来自命题方金融库，一个字没改</div>
                    <div class="pol-guard-l">主题标签与匹配打分：从门槛和特点的原文派生，用于过筛</div>
                    <div class="pol-guard-l">原表写「根据企业实际情况不定」的，页面显示「以机构核定为准」，管家不替银行报数</div>
                </div>`;""",
    "body += `" + ev_panel([
        ("原文照抄", "机构、产品名、适用门槛、核心特点、额度、期限、利率，原样来自命题方金融库", False),
        ("规则派生", "主题标签与匹配打分，从门槛和特点的原文派生，只用于过筛", False),
        ("不生成", "原表写「根据企业实际情况不定」的，显示「以机构核定为准」，管家不替银行报数", True),
    ]) + "`;", "金融页数据边界")

rep("""html += `<div class="pol-guard">
                <div class="pol-guard-t">这页的数据边界</div>
                <div class="pol-guard-l">政策与金融条目全部来自命题方两个库，名称、额度、期限、利率原文照抄</div>
                <div class="pol-guard-l">申报条件、截止日期，以及原表写「根据企业实际情况不定」的额度利率，管家不生成</div>
                <div class="pol-guard-l">排序是规则打分，不是中签概率，命中理由每条都摆在卡片上</div>
            </div>`;""",
    "html += `" + ev_panel([
        ("原文照抄", "政策与金融条目全部来自命题方两个库，名称、额度、期限、利率一字不改", False),
        ("规则派生", "排序是规则打分，不是中签概率，命中理由每条都摆在卡片上", False),
        ("不生成", "申报条件、截止日期，以及原表写「根据企业实际情况不定」的额度利率，管家不生成", True),
    ]) + "`;", "找机会页数据边界")

# ============================================================
# B. 图标 helper + tab 路由 + 管公司分栏
# ============================================================
rep("""    <script>
        // ===== State =====""",
    """    <script>
        // 内联图标 helper：全部走顶部的 SVG symbol，零外部请求
        function ic(name, size) { return '<svg class="ic ic-' + (size || 18) + '"><use href="#i-' + name + '"></use></svg>'; }

        // ===== State =====""", "图标 helper")

rep("""            const screens = {
                home: 'screenHome',
                service: 'screenService',
                circle: 'screenCircle',
                profile: 'screenProfile',   // 不再占底部位置，从首页右上角头像进
                opportunity: 'screenOpportunity',
                risk: 'screenRisk',
            };""",
    """            const screens = {
                home: 'screenHome',
                company: 'screenCompany',   // 原「服务」与原「风险」并成这一页
                circle: 'screenCircle',
                profile: 'screenProfile',   // 不再占底部位置，从首页右上角头像进
                opportunity: 'screenOpportunity',
            };""", "tab 路由表")

rep("""            if (tab === 'opportunity') renderOpportunityTab();
            if (tab === 'risk') renderRiskTab();""",
    """            if (tab === 'opportunity') renderOpportunityTab();
            if (tab === 'company') renderRiskTab();""", "切到管公司时刷风险")

rep("""        // ===== 风险一览全屏页 =====
        // 服务页和首页的风险入口现在直接切到风险 tab
        function openRiskPage() {
            switchTab('risk');
        }""",
    """        // ===== 风险：并进管公司页的「合规风险」栏 =====
        function openRiskPage() {
            switchTab('company');
            setCompanySection('risk');
        }

        // 管公司页两栏切换：经营事项 / 合规风险
        function setCompanySection(which) {
            const biz = document.getElementById('cmBizPane');
            const risk = document.getElementById('riskScroll');
            if (!biz || !risk) return;
            const isRisk = which === 'risk';
            biz.style.display = isRisk ? 'none' : 'flex';
            risk.style.display = isRisk ? 'flex' : 'none';
            document.getElementById('cmSegBiz').classList.toggle('on', !isRisk);
            document.getElementById('cmSegRisk').classList.toggle('on', isRisk);
            if (isRisk) renderRiskTab();
        }

        // 更多服务：无数据支撑的演示项收在折叠区里，有真数据的顶上去
        function toggleMoreServices() {
            const box = document.getElementById('moreServices');
            const tg = document.getElementById('moreToggle');
            if (!box || !tg) return;
            const open = box.style.display !== 'none';
            box.style.display = open ? 'none' : 'grid';
            tg.classList.toggle('open', !open);
        }""", "管公司分栏与折叠")

# 风险角标：只在有高风险时亮，同时挂 tab 与分栏
rep("""            const badge = document.getElementById('riskBadge');
            if (badge) badge.textContent = rp.alerts.length + boardRisks.length;
            if (!box) return;""",
    """            // 角标只数高风险，没有高风险就不亮，避免常年挂个红点
            const highs = rp.alerts.filter(a => a.lv === 'high').length + boardRisks.filter(r => r.level === 'high').length;
            const badge = document.getElementById('riskBadge');
            if (badge) badge.textContent = highs > 0 ? highs : '';
            const seg = document.getElementById('cmRiskBadge');
            if (seg) { seg.textContent = highs > 0 ? highs : ''; seg.classList.toggle('on', highs > 0); }
            if (!box) return;""", "风险角标只数高风险")

# 首页三张统计卡：风险那张改跳管公司
rep("""                    <div class="st-card" onclick="scrollToBoard('bdRiskList')">
                        <div class="st-num st-warn">${boardRisks.length}</div><div class="st-label">风险提示</div>
                    </div>""",
    """                    <div class="st-card" onclick="openRiskPage()">
                        <div class="st-num st-warn">${boardRisks.length}</div><div class="st-label">风险提示</div>
                    </div>""", "风险统计卡改跳管公司")

# ============================================================
# C. 「我要办的事」入口
# ============================================================
TASK_JS = """
        // ===== 首页「我要办的事」入口 =====
        // 按用户嘴里说得出来的话分类，不按部门分。每条标清背后有没有命题方的真数据。
        const TASK_ENTRIES = [
            { key: '开公司', label: '我要开公司', icon: 'biz',      desc: '核名、主体类型、注册、刻章、开户', src: 'generic' },
            { key: '社保',   label: '我要交社保', icon: 'shield',   desc: '社保开户、按月缴费、公积金提取', src: 'generic' },
            { key: '报税',   label: '我要报税',   icon: 'receipt',  desc: '税务登记、票种核定、按期申报', src: 'generic' },
            { key: '政策',   label: '我要政策补助', icon: 'doc',    desc: '拿你的档案逐条比对政策库', src: 'lib' },
            { key: '找钱',   label: '我要找钱',   icon: 'coin',     desc: '按适用门槛过筛金融产品', src: 'lib' },
            { key: '知产',   label: '我要办知识产权', icon: 'award', desc: '专利商标软著 + 库内资助贴息', src: 'mixed' },
            { key: '场地',   label: '我要找场地', icon: 'pin',      desc: '北辰四大园区 + 园区载体政策', src: 'mixed' },
            { key: '招人',   label: '我要招人',   icon: 'users',    desc: '用工合规 + 人才支持政策', src: 'mixed' },
        ];

        // 库内条数一律现算，不写死
        function policyTagCount(tag) {
            return POLICY_DOCS.concat(POLICY_READS).filter(p => (p.tags || []).indexOf(tag) >= 0).length;
        }
        function finTagCount(tag) {
            return FIN_PRODUCTS.filter(p => (p.tags || []).indexOf(tag) >= 0).length;
        }
        function taskEvidence(key) {
            if (key === '政策') return { cls: 'ev-lib', text: '库内 ' + (POLICY_DOCS.length + POLICY_READS.length) + ' 条' };
            if (key === '找钱') return { cls: 'ev-lib', text: '库内 ' + (FIN_PRODUCTS.length + FIN_SUBSIDIES.length) + ' 条' };
            if (key === '知产') return { cls: 'ev-lib', text: '库内 ' + (policyTagCount('知识产权') + finTagCount('知识产权') + 2) + ' 条' };
            if (key === '场地') return { cls: 'ev-lib', text: '库内 ' + policyTagCount('园区载体') + ' 条' };
            if (key === '招人') return { cls: 'ev-lib', text: '库内 ' + policyTagCount('人才支持') + ' 条' };
            return { cls: 'ev-none', text: '通用流程' };
        }

        // 排序跟着画像走：还没注册主体的先看开公司，已有主体的先看政策和钱
        function taskOrder() {
            const top = state.company === '未注册' ? ['开公司', '政策', '招人'] : ['政策', '找钱', '知产'];
            const rest = TASK_ENTRIES.map(t => t.key).filter(k => top.indexOf(k) < 0);
            return top.concat(rest);
        }

        function renderTaskGrid() {
            const box = document.getElementById('taskGrid');
            if (!box) return;
            const order = taskOrder();
            box.innerHTML = order.map((k, i) => {
                const t = TASK_ENTRIES.filter(x => x.key === k)[0];
                if (!t) return '';
                const ev = taskEvidence(k);
                return `<div class="task-card${i < 2 ? ' tk-top' : ''}" onclick="taskGo('${t.key}')">
                    <span class="task-ic">${ic(t.icon, 20)}</span>
                    <div class="task-t">${t.label}</div>
                    <div class="task-d">${t.desc}</div>
                    <div class="task-foot"><span class="ev-badge ${ev.cls}">${ev.text}</span></div>
                </div>`;
            }).join('');
        }

        function taskGo(key) {
            if (key === '政策') { openServiceDetail('政策补贴'); return; }
            if (key === '找钱') { finTab = 'debt'; openServiceDetail('金融服务'); return; }
            openTaskPage(key);
        }

        // ===== 办事详情页 =====
        // 命题方没给数据的三类（开公司 / 社保 / 报税）：只讲办事顺序，
        // 全页不出现时限、费用、截止日，页顶必须顶着「通用流程口径」的横幅。
        const TASK_PAGES = {
            '开公司': {
                title: '我要开公司', icon: 'biz', generic: true,
                lead: '从没有主体到能对外签约收款，一般要走完下面五步。顺序可以微调，少一步就会卡在后面。',
                steps: [
                    { t: '核名', d: '定公司名与经营范围，提交名称预先核准' },
                    { t: '定主体类型', d: '有限责任公司、个人独资、合伙企业，责任承担与税负口径不一样，先想清楚再报' },
                    { t: '设立登记', d: '提交章程、股东与法定代表人材料，领营业执照' },
                    { t: '刻章备案', d: '公章、财务章、法人章、发票章' },
                    { t: '银行开户', d: '开对公基本户，之后才能走对公收付' },
                ],
                todos: ['准备核名材料，定 3 个备选公司名', '确定主体类型与股权结构', '预约银行开对公户'],
            },
            '社保': {
                title: '我要交社保', icon: 'shield', generic: true,
                lead: '有了主体、招了第一个人，社保这条线就要开起来。公积金与社保是两套经办口径，分开办。',
                steps: [
                    { t: '社保单位开户', d: '用营业执照与银行信息办单位参保登记' },
                    { t: '公积金单位开户', d: '与社保分开办理，经办机构不同' },
                    { t: '员工增减员申报', d: '入职当月增员，离职当月减员' },
                    { t: '按期缴费', d: '缴费基数与申报期以社保经办机构公告为准，管家不替你猜' },
                    { t: '公积金提取', d: '租房、购房、离职等情形按经办机构要求提交材料' },
                ],
                todos: ['办理社保单位开户', '办理公积金单位开户', '确认首次增员名单'],
            },
            '报税': {
                title: '我要报税', icon: 'receipt', generic: true,
                lead: '拿到执照之后税务这条线就开始计时了。没有业务也要按期做零申报，漏了会有异常记录。',
                steps: [
                    { t: '税务登记信息确认', d: '确认登记信息、财务负责人、办税人员' },
                    { t: '票种核定与领用', d: '按业务类型申请票种和额度' },
                    { t: '记账建账', d: '自己记或找代账，凭证与账簿要留存备查' },
                    { t: '按期申报', d: '申报期、税率、优惠口径以税务机关公告为准，管家不生成具体日期' },
                    { t: '年度汇算清缴', d: '年度终了后按规定完成企业所得税汇算' },
                ],
                todos: ['确认税务登记与办税人员信息', '申请票种核定', '确定记账方式：自己记还是找代账'],
            },
            '知产': {
                title: '我要办知识产权', icon: 'award',
                lead: '左边是办事顺序，右边挂的是命题方库里真有的资助与贴息条目，点进去看原文。',
                genericNote: '下面这四类的办理顺序属于通用流程口径，周期与费用命题方未提供，不生成。',
                steps: [
                    { t: '发明专利', d: '撰写、提交、实质审查、答复审查意见' },
                    { t: '实用新型与外观设计', d: '形式审查为主，与发明专利可组合布局' },
                    { t: '商标注册', d: '先查询近似，再按类别提交' },
                    { t: '软件著作权', d: '提交源代码与说明文档登记' },
                ],
                policyTag: '知识产权', finTag: '知识产权', subsidyKw: '知识产权',
                todos: ['盘点已有技术方案，定专利布局清单', '核名通过后尽早提交商标申请'],
            },
            '场地': {
                title: '我要找场地', icon: 'pin',
                lead: '北辰产业云社区四大园区，名称与产业方向取自命题方材料。',
                parkNote: '面积、租金、入驻条件与补贴，命题方材料未提供，以园区招商口径为准，管家不生成。',
                parks: [
                    { n: '朝阳数据要素产业园', d: '数据要素方向' },
                    { n: '人工智能会展产业园', d: '人工智能与会展方向' },
                    { n: '智能机器人创新应用基地', d: '智能机器人方向' },
                    { n: '北辰 AI 超维社区', d: 'AI 应用社区方向' },
                ],
                policyTag: '园区载体',
                todos: ['联系园区企服中心问入驻条件与可租面积'],
            },
            '招人': {
                title: '我要招人', icon: 'users',
                lead: '招第一个人之前先把用工合规的底铺好，后面补比一开始就做贵得多。',
                genericNote: '下面四条属于通用用工合规口径，命题方数据库未覆盖，具体要求以人社部门公告为准。',
                steps: [
                    { t: '签书面劳动合同', d: '入职即签，岗位、薪酬、工作地点写清楚' },
                    { t: '办理社保参保', d: '与社保单位开户那条线衔接' },
                    { t: '建考勤与工资台账', d: '发薪记录与考勤留痕，争议时是关键证据' },
                    { t: '规章制度公示', d: '制度要经过公示或告知程序才对员工有约束力' },
                ],
                policyTag: '人才支持',
                todos: ['准备劳动合同模板', '确认社保参保流程已跑通'],
            },
        };

        let currentTaskKey = '';

        function openTaskPage(key) {
            const d = TASK_PAGES[key];
            if (!d) return;
            currentTaskKey = key;
            document.getElementById('pageTitle').innerHTML = ic(d.icon, 18) + ' ' + d.title;
            document.getElementById('pageScroll').innerHTML = renderTaskPage(key);
            document.getElementById('pageOverlay').classList.add('active');
        }

        function renderTaskPage(key) {
            const d = TASK_PAGES[key];
            let h = '';

            if (d.generic) {
                h += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">通用流程口径，非政策原文</div>
                    <div class="ev-generic-d">这一类命题方数据库没有提供数据。下面只讲办事顺序，不写办理时限、费用和截止日期，一切以受理机关公告为准。</div>
                </div>`;
            }
            h += `<div class="tp-lead">${d.lead}</div>`;

            if (d.parks) {
                h += `<div class="page-section-title">北辰产业云社区四大园区</div>`;
                h += d.parks.map(p => `<div class="tp-park">
                    <div class="tp-park-n">${p.n}</div>
                    <div class="tp-park-d">${p.d}</div>
                </div>`).join('');
                h += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">园区名称来自命题方材料</div>
                    <div class="ev-generic-d">${d.parkNote}</div>
                </div>`;
            }

            if (d.steps) {
                h += `<div class="page-section-title">${d.generic ? '办事顺序' : '办理顺序'}</div>`;
                h += '<div class="tp-steps">' + d.steps.map((s, i) => `
                    <div class="tp-step">
                        <span class="tp-no">${i + 1}</span>
                        <div><div class="tp-t">${s.t}</div><div class="tp-d">${s.d}</div></div>
                    </div>`).join('') + '</div>';
                if (d.genericNote) {
                    h += `<div class="ev-generic">${ic('info', 18)}<div>
                        <div class="ev-generic-t">通用流程口径，非政策原文</div>
                        <div class="ev-generic-d">${d.genericNote}</div>
                    </div>`;
                }
            }

            if (d.todos && d.todos.length) {
                h += `<div class="tp-cta" onclick="taskToPlan('${key}')">${ic('plus', 16)}把这几件事加进我的待办</div>`;
                h += `<div class="tp-note">加进去的是事项本身，不带日期。办理时限以受理机关公告为准，管家不替你预设截止日。</div>`;
            }

            // 库内条目：政策、金融产品、可叠加贴息，全部可点开原文
            if (d.policyTag) {
                const hits = POLICY_DOCS.concat(POLICY_READS).filter(p => (p.tags || []).indexOf(d.policyTag) >= 0);
                h += `<div class="page-section-title">命题方政策库 · ${d.policyTag} ${hits.length} 条</div>`;
                h += hits.length ? hits.slice(0, 8).map(p => policyCard(p, false)).join('')
                                 : '<div class="pol-empty">政策库里没有这个标签的条目，不编一条出来。</div>';
                if (hits.length > 8) h += `<div class="pol-count">还有 ${hits.length - 8} 条，去政策页看全库</div>`;
            }
            if (d.finTag) {
                const fh = FIN_PRODUCTS.filter(p => (p.tags || []).indexOf(d.finTag) >= 0);
                h += `<div class="page-section-title">命题方金融库 · ${d.finTag} ${fh.length} 个产品</div>`;
                h += fh.length ? fh.map(finCard).join('') : '<div class="pol-empty">金融库里没有这个标签的产品。</div>';
            }
            if (d.subsidyKw) {
                const sh = FIN_SUBSIDIES.filter(s => s.type.indexOf(d.subsidyKw) >= 0);
                if (sh.length) {
                    h += `<div class="page-section-title">可叠加的贴息补贴 ${sh.length} 条</div>`;
                    h += sh.map(s => subsidyCard(s, true)).join('');
                }
            }

            const rows = [];
            if (d.policyTag || d.finTag) rows.push(['原文照抄', '本页库内条目的名称、机构、额度、期限、利率来自命题方两个库，一字未改', false]);
            if (d.parks) rows.push(['原文照抄', '四个园区名称与产业方向取自命题方《北辰产业云社区》材料', false]);
            rows.push(['通用口径', '办事顺序为通用流程，非政策原文，不作为办理依据', true]);
            rows.push(['不生成', '办理时限、费用、截止日期、申报条件，管家一律不生成', true]);
            h += '<div class="ev-panel"><div class="ev-panel-t">' + ic('file', 16) + '这页的数据边界</div>'
               + rows.map(r => `<div class="ev-line${r[2] ? ' k-none' : ''}"><span class="ev-key">${r[0]}</span><span class="ev-val">${r[1]}</span></div>`).join('')
               + '</div>';
            return h;
        }

        // 一键把办事清单写进看板待办。只写事项不写日期，日期由用户自己定。
        function taskToPlan(key) {
            const d = TASK_PAGES[key];
            if (!d || !d.todos) return;
            let added = 0;
            d.todos.forEach(function (t) {
                if (!boardTodos.filter(x => x.text === t).length) {
                    boardTodos.push({ text: t, meta: '自定时间 · 来自「' + d.title + '」', scene: 'industry', urgent: false, completed: false });
                    added++;
                }
            });
            renderBoard();
            showToast(added ? '已加 ' + added + ' 项到待办，时间你自己定' : '这几项已经在待办里了');
        }
"""
rep("        // ===== 机会页 =====", TASK_JS + "\n        // ===== 机会页 =====", "办事入口与办事详情页")

# 看板重算时一并重排办事入口（画像变了顺序要跟着变）
rep("""            renderRiskTab();      // 风险 tab 的角标与列表跟着看板一起刷
            if (state.currentTab === 'opportunity') renderOpportunityTab();""",
    """            renderRiskTab();      // 合规风险栏的角标与列表跟着看板一起刷
            renderTaskGrid();     // 办事入口的排序与库内条数跟着画像重算
            if (state.currentTab === 'opportunity') renderOpportunityTab();""", "看板联动办事入口")

# ============================================================
# D. servicePages 重写 + serviceDetails 整块删（已是死代码）
# ============================================================
NEW_SERVICE_PAGES = """        // 通用服务独立页数据。icon 存的是 SVG symbol 名字，不是 emoji。
        // generic:true 的页面顶部会顶一条「演示内容」横幅，说清背后没有命题方数据。
        const servicePages = {
            '政策补贴': { icon: 'doc', dynamic: true },   // 内容由 renderPolicyPage 现算，见政策匹配引擎
            '金融服务': { icon: 'bank', dynamic: true },  // 走 renderFinancePage 的贷款融资页
            '融资机会': { icon: 'coin', dynamic: true },  // 走 renderFinancePage 的股权与投行页
            '行政日历': { icon: 'calendar', dynamic: true },
            '开单诊断': {
                icon: 'check', demo: true,
                sections: [
                    { title: '开单合规检查', items: [
                        { icon: 'check', title: '营业执照', desc: '已办理', badge: '完成' },
                        { icon: 'check', title: '税务登记', desc: '已登记', badge: '完成' },
                        { icon: 'alert', title: '社保开户', desc: '状态待确认', badge: '待办' },
                        { icon: 'doc', title: '公积金开户', desc: '未办理', badge: '待办' },
                    ]},
                ],
                cta: '开始全面体检',
            },
            '云服务规划': {
                icon: 'cloud', demo: true,
                sections: [
                    { title: '创业云资源', items: [
                        { icon: 'server', title: '云服务器', desc: '轻量应用服务器' },
                        { icon: 'globe', title: '域名', desc: '.com/.cn 域名注册' },
                        { icon: 'bolt', title: '算力与 GPU', desc: '按需付费，AI 训练可用' },
                        { icon: 'card', title: '收款通道', desc: '聚合支付对接' },
                        { icon: 'phone', title: '短信与验证码', desc: '三网合一，按条计费' },
                    ]},
                ],
                cta: '生成云架构方案',
            },
            '五险一金': {
                icon: 'shield', demo: true,
                sections: [
                    { title: '服务功能', items: [
                        { icon: 'calendar', title: '缴费日历', desc: '按月提醒，基数与截止日以经办机构公告为准' },
                        { icon: 'coin', title: '失业金申领', desc: '符合条件可线上申领' },
                        { icon: 'home', title: '公积金提取', desc: '租房、购房、离职提取' },
                        { icon: 'chart', title: '退休规划测算', desc: '演示功能' },
                    ]},
                ],
                cta: '查看缴费基数说明',
            },
            '找顾问': {
                icon: 'scale', demo: true,
                sections: [
                    { title: '顾问类型', items: [
                        { icon: 'biz', title: '工商注册顾问', desc: '注册、变更、注销' },
                        { icon: 'chart', title: '财税记账顾问', desc: '代理记账、报税' },
                        { icon: 'scale', title: '法律顾问', desc: '合同、合规' },
                        { icon: 'award', title: '专利代理人', desc: '专利申请、答复' },
                    ]},
                ],
                cta: '一键联系顾问',
            },
            '出海去': {
                icon: 'globe', demo: true,
                sections: [
                    { title: '目的地政策', items: [
                        { icon: 'globe', title: '新加坡', desc: '政策友好，金融与科技方向' },
                        { icon: 'globe', title: '美国', desc: '市场大，合规要求高' },
                        { icon: 'globe', title: '日本', desc: '消费稳定，本地化门槛高' },
                    ]},
                    { title: '合规服务', items: [
                        { icon: 'check', title: '出海合规诊断', desc: '商标、税务、数据合规一站式排查' },
                    ]},
                ],
                cta: '启动出海业务',
            },
        };
"""
cut("        // 通用服务独立页数据\n        const servicePages = {", "        // ===== 行政日历（月历） =====",
    NEW_SERVICE_PAGES + "\n", "重写 servicePages")

# serviceDetails 整块删（openServiceDetail 里 servicePages 优先，这块从来走不到）
cut("        const serviceDetails = {", "\n\n        // ===== 金融库", "", "删死代码 serviceDetails")
rep("""            const data = serviceDetails[serviceName] || {
                icon: '📄',
                title: serviceName,
                sub: '更多信息',
                content: '<div class="mc-item">功能建设中，敬请期待</div>'
            };
            document.getElementById('modalTitle').textContent = data.icon + ' ' + data.title;
            document.getElementById('modalSub').textContent = data.sub;
            document.getElementById('modalContent').innerHTML = data.content;""",
    """            document.getElementById('modalTitle').innerHTML = ic('info', 18) + ' ' + serviceName;
            document.getElementById('modalSub').textContent = '更多信息';
            document.getElementById('modalContent').innerHTML = '<div class="mc-item">这一项还没有数据支撑，先不做演示。</div>';""",
    "服务弹层兜底")

# renderServicePage：图标改 SVG，演示页顶横幅
rep("""            const data = servicePages[name];
            if (!data) return;
            document.getElementById('pageTitle').textContent = data.icon + ' ' + name;
            let html = '';
            if (data.overview) {
                html += `<div class="page-overview">
                    <span class="po-icon">${data.overview.icon}</span>
                    <div class="po-text">
                        <div class="po-label">${data.overview.label}</div>
                        <div class="po-value">${data.overview.value}</div>
                    </div>
                </div>`;
            }
            (data.sections || []).forEach(section => {
                html += `<div class="page-section-title">${section.title}</div>`;
                section.items.forEach(item => {
                    html += `<div class="page-card">
                        <span class="pg-icon">${item.icon}</span>""",
    """            const data = servicePages[name];
            if (!data) return;
            document.getElementById('pageTitle').innerHTML = ic(data.icon, 18) + ' ' + name;
            let html = '';
            if (data.demo) {
                html += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">演示内容，无命题方数据支撑</div>
                    <div class="ev-generic-d">这一页命题方数据库没有覆盖，内容用于演示交互，不作为办理依据。有真数据的是政策补贴、金融服务、融资机会，以及办事入口里的知识产权、找场地、招人。</div>
                </div>`;
            }
            (data.sections || []).forEach(section => {
                html += `<div class="page-section-title">${section.title}</div>`;
                section.items.forEach(item => {
                    html += `<div class="page-card">
                        <span class="pg-icon">${ic(item.icon, 20)}</span>""", "服务页图标与演示横幅")

# 行政日历：演示数据横幅 + 去 emoji
rep("""            document.getElementById('pageTitle').textContent = '📅 行政日历';
            document.getElementById('pageScroll').innerHTML = `
                <div class="cal-card">""",
    """            document.getElementById('pageTitle').innerHTML = ic('calendar', 18) + ' 行政日历';
            document.getElementById('pageScroll').innerHTML = `
                <div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">日程为演示数据</div>
                    <div class="ev-generic-d">这里的日期用于演示小事引擎的写入与勾销，不来自命题方政策库或金融库，不作为申报或缴费依据。</div>
                </div>
                <div class="cal-card">""", "行政日历演示横幅")
rep('<div class="page-section-title">📌 日程安排</div>', '<div class="page-section-title">日程安排</div>', "日程安排标题")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第二趟完成")

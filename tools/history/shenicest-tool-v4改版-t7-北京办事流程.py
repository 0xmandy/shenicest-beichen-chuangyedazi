# -*- coding: utf-8 -*-
"""第七趟：办事流程换成北京官方口径、经营事项按政务大厅顺序重排、猜您需要去掉来源标签。

办事流程出处（2026-08-27 检索）：
- 企业开办：北京市企业服务 e 窗通平台，营业执照 / 免费公章 / 涉税事项 / 五险一金信息采集 / 银行预约开户一网通办，一天办结
  scjgj.beijing.gov.cn 开办企业一网通办、e 窗通使用指南、开办企业 4.0 版政策解读
- 社保与公积金：北京市人力资源和社会保障局。e 窗通新设单位社保登记随注册同步，无需单独登记；
  未同步的在社保网上服务平台填报。公积金单位登记开户在同一平台「单位预登记」，第二个工作日完成开户。
  社会保险、就业、劳动用工备案为统一登记。rsj.beijing.gov.cn / gjj.beijing.gov.cn
- 税务与发票：北京市电子税务局。税（费）种认定、网签三方协议、发票票种核定初次申请、
  税控设备（税务 UKey）申领、首次发票申领有份数上限。beijing.chinatax.gov.cn
- App 与小程序：工信部信管〔2023〕105 号，境内 App 主办者须备案，未备案不得从事 App 互联网信息服务；
  小程序由运行平台初审后报工信部，同主体同名称上架多平台需逐平台备案；省级通信管理局二十个工作日内审核
- 生成式 AI：《生成式人工智能服务管理暂行办法》，具有舆论属性或社会动员能力的服务经属地网信部门备案；
  已上线应用须在显著位置或产品详情页公示所用已备案模型名称与备案号。cac.gov.cn
"""
import io, sys

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-2026-08-27.html"
src = io.open(PATH, encoding="utf-8").read()

def rep(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit("锚点[%s]命中 %d 次，应为 1 次，退出" % (label, n))
    src = src.replace(old, new, 1)
    print("  ok  %s" % label)

def cut(start, end, new, label):
    global src
    if src.count(start) != 1 or src.count(end) != 1:
        sys.exit("区间锚点[%s]不唯一，退出" % label)
    i = src.index(start); j = src.index(end)
    if j <= i: sys.exit("区间锚点[%s]顺序不对" % label)
    src = src[:i] + new + src[j:]
    print("  ok  %s" % label)

# ============================================================
# 1 猜您需要：去掉来源标签，只留插画与事项名
# ============================================================
rep("""                return `<div class="task-card${i < 3 ? ' tk-top' : ''}" onclick="taskGo('${t.key}')">
                    <svg class="capy"><use href="#capy-${t.capy}"></use></svg>
                    <div class="task-t">${t.label}</div>
                    <div class="task-ev${ev.lib ? '' : ' tk-generic'}">${ev.text}</div>
                </div>`;""",
    """                return `<div class="task-card${i < 3 ? ' tk-top' : ''}" onclick="taskGo('${t.key}')">
                    <svg class="capy"><use href="#capy-${t.capy}"></use></svg>
                    <div class="task-t">${t.label}</div>
                </div>`;""", "猜您需要去标签")
rep("""                if (!t) return '';
                const ev = taskEvidence(k);
""", """                if (!t) return '';
""", "去掉标签取值")
rep("""        function taskEvidence(key) {
            if (key === '政策') return { lib: true, text: '库内 ' + (POLICY_DOCS.length + POLICY_READS.length) + ' 条' };
            if (key === '融资') return { lib: true, text: '库内 ' + (FIN_PRODUCTS.length + FIN_SUBSIDIES.length) + ' 条' };
            if (key === '场地') return { lib: true, text: '库内 ' + policyTagCount('园区载体') + ' 条' };
            if (key === '出海') return { lib: true, text: '库内 ' + (policyTagCount('企业出海') + finTagCount('跨境出海')) + ' 条' };
            if (key === 'aigc') return { lib: true, text: '库内 ' + policyTagCount('人工智能') + ' 条' };
            return { lib: false, text: '通用流程' };
        }

""", "", "删来源标函数")
rep("""        .task-ev { font-size: 10px; line-height: 1.5; font-weight: 600; color: var(--brand); }
        .task-ev.tk-generic { color: var(--n400); font-weight: 500; }""",
    """        /* 交社保这类要按政府口径分情况的，用这张小卡摆出来 */
        .tp-case { margin: 0 20px 9px; padding: 12px 14px; background: var(--n0); border: var(--hair); border-left: 3px solid var(--brand); border-radius: var(--r-sm); }
        .tp-case-t { font-size: var(--fs-md); font-weight: 600; color: var(--n900); line-height: 1.45; }
        .tp-case-d { font-size: var(--fs-sm); color: var(--n500); line-height: 1.75; margin-top: 4px; }
        .tp-where { margin: 0 20px 14px; padding: 11px 14px; background: var(--brand-50); border-radius: var(--r-sm); font-size: var(--fs-sm); color: var(--brand); line-height: 1.7; }""",
    "情况卡与办理入口样式")

# ============================================================
# 2 办事详情页：换成北京官方口径，去掉所有口径横幅与数据边界
# ============================================================
NEW_TASK_PAGES = """        // ===== 办事详情页 =====
        // 流程取自北京市官方口径，出处见 shenicest-tool-v3改版-t7-北京办事流程.py 头部注释
        const TASK_PAGES = {
            '开公司': {
                title: '开公司', icon: 'biz',
                lead: '北京开办企业走「e 窗通」一网通办：营业执照、免费公章、涉税事项、五险一金信息采集、银行预约开户在一个平台一次填报，一天办结。',
                steps: [
                    { t: '名称自主申报', d: '在 e 窗通 先把公司名报上，同时把经营范围想清楚' },
                    { t: '设立登记', d: '提交章程、股东与法定代表人信息，实名认证后申请营业执照' },
                    { t: '免费刻章', d: '开办环节的公章由政府买单，跟执照一起做' },
                    { t: '涉税事项', d: '同一份表里同步做税务信息确认与票种核定申请' },
                    { t: '五险一金信息采集', d: '员工参保信息在这一步一并填，社保登记会随注册同步过去' },
                    { t: '银行预约开户', d: '平台上直接预约合作银行，执照下来就能去开对公户' },
                ],
                where: '北京市企业服务 e 窗通平台。执照、公章、发票与税控设备打包成「办理结果」服务包，可以邮寄，也可以到企业开办大厅一窗领取。',
                todos: ['在 e 窗通 提交名称自主申报', '备齐章程与股东身份材料', '预约银行开对公户'],
            },
            '社保': {
                title: '交社保', icon: 'shield',
                lead: '先看你的单位是怎么成立的，这一步决定了你要不要单独跑社保登记。',
                cases: [
                    { t: '通过 e 窗通 新设的单位', d: '社保登记已经随注册同步完成，不用再单独登记。直接进社保网上服务平台做增员就行。' },
                    { t: '数据没同步，或者早年成立的单位', d: '要在北京市社会保险网上服务平台按页面提示填报信息、上传材料，单独办单位参保登记。' },
                ],
                steps: [
                    { t: '确认社保登记状态', d: '登社保网上服务平台看得到单位信息，就说明已经同步，不用重复办' },
                    { t: '单位参保登记', d: '没同步的才办，在平台填报并上传材料' },
                    { t: '公积金单位开户', d: '在平台「单位预登记」录缴存比例、经办人、缴款方式等登记信息，系统在第二个工作日完成开户与网上业务系统注册' },
                    { t: '增减员申报', d: '社会保险、就业、劳动用工备案是统一登记，员工入职一次填报三件事一起办' },
                    { t: '按月缴费', d: '缴费基数与申报期以社保经办机构当期公告为准' },
                ],
                where: '北京市社会保险网上服务平台，从北京市人力资源和社会保障局官网首页「社保网上服务」进。公积金登记开户在同一平台。',
                todos: ['确认社保登记是否已随注册同步', '办理公积金单位开户', '把首批员工做增员申报'],
            },
            '报税': {
                title: '报税', icon: 'receipt',
                lead: '执照拿到手税务这条线就开始计时了。北京走电子税务局，多数事项在线上办完，不用跑大厅。',
                steps: [
                    { t: '税（费）种认定', d: '电子税务局「我要办税 → 综合信息报告 → 税（费）种认定」，按提示填报提交' },
                    { t: '网签三方协议', d: '「我要办税 → 其他服务事项 → 网签三方协议」，签完才能从对公户扣缴税款' },
                    { t: '票种核定', d: '「我要办税 → 发票使用 → 发票票种核定 → 票种核定初次申请」，按业务选票种' },
                    { t: '税控设备申领', d: '票种核定审核通过后在事项进度里申请，盘类型选税务 UKey' },
                    { t: '按期申报', d: '没有业务也要按期做零申报，漏了会留异常记录。申报期与税率以税务机关公告为准' },
                    { t: '年度汇算清缴', d: '年度终了后按规定完成企业所得税汇算' },
                ],
                where: '北京市电子税务局。首次办税前先确认办税人员与财务负责人信息已经维护好。',
                todos: ['完成税（费）种认定', '网签三方协议', '确定记账方式：自己记还是找代账'],
            },
            '发票': {
                title: '开发票', icon: 'receipt',
                lead: '能不能开票、能开什么票，决定你能接什么样的客户。这条线和税务登记是同一套系统，票种核定通过之后才能领用开具。',
                steps: [
                    { t: '票种核定初次申请', d: '电子税务局「发票使用 → 发票票种核定」，按业务类型选所需票种' },
                    { t: '税控设备申领', d: '核定通过后在事项进度里线上申领，盘类型选税务 UKey' },
                    { t: '首次发票申领', d: '首次申领的份数有上限，用完再按增量规则申请提额' },
                    { t: '开具与红冲', d: '开错了按规定红冲，跨期的不能直接作废' },
                    { t: '进销项凭证留存', d: '取得的进项发票与开出的销项发票都要归档备查' },
                ],
                where: '北京市电子税务局。开票信息模板（名称、税号、地址电话、开户行账号）提前整理好，能省不少来回。',
                todos: ['提交票种核定初次申请', '申领税务 UKey', '整理常用开票信息模板'],
            },
            '招人': {
                title: '招人用工', icon: 'users',
                lead: '北京把社会保险、就业、劳动用工备案做成了统一登记，招第一个人的时候三件事在一个入口一起办。',
                steps: [
                    { t: '签书面劳动合同', d: '入职即签，岗位、薪酬、工作地点写清楚' },
                    { t: '统一登记做增员', d: '社会保险、就业、劳动用工备案统一登记，一次填报三件事一起办' },
                    { t: '建考勤与工资台账', d: '发薪记录与考勤留痕，起争议时是关键证据' },
                    { t: '规章制度公示', d: '制度要经过公示或告知程序才对员工有约束力' },
                ],
                where: '北京市社会保险网上服务平台，单位用户「在职职工管理」里做增减员。',
                policyTag: '人才支持',
                todos: ['准备劳动合同模板', '在社保平台完成首次增员', '把规章制度做公示留痕'],
            },
            '知产': {
                title: '知识产权', icon: 'award',
                lead: '技术方案、品牌名、代码，能确权的尽早确权。下面挂的是可以申请的资助与质押贴息条目。',
                steps: [
                    { t: '发明专利', d: '撰写、提交、实质审查、答复审查意见' },
                    { t: '实用新型与外观设计', d: '形式审查为主，可以和发明专利组合布局' },
                    { t: '商标注册', d: '先查询近似，再按类别提交。核名过了就尽早报商标' },
                    { t: '软件著作权', d: '提交源代码与说明文档登记，多数应用商店把它当上架前置' },
                ],
                policyTag: '知识产权', finTag: '知识产权', subsidyKw: '知识产权',
                todos: ['盘点已有技术方案，定专利布局清单', '提交商标注册申请', '给核心代码做软著登记'],
            },
            '场地': {
                title: '找场地', icon: 'pin',
                lead: '北辰产业云社区四大园区，按产业方向选。下面挂的是园区载体相关的支持政策。',
                parks: [
                    { n: '朝阳数据要素产业园', d: '数据要素方向' },
                    { n: '人工智能会展产业园', d: '人工智能与会展方向' },
                    { n: '智能机器人创新应用基地', d: '智能机器人方向' },
                    { n: '北辰 AI 超维社区', d: 'AI 应用社区方向' },
                ],
                where: '可租面积、租金与入驻条件问园区企服中心，不同园区口径不一样。',
                policyTag: '园区载体',
                todos: ['联系园区企服中心问入驻条件与可租面积', '对比四个园区的产业方向'],
            },
            '出海': {
                title: '出海', icon: 'globe',
                lead: '出海要同时过三关：主体与架构、资金进出、数据与内容合规。下面挂的是出海与跨境相关的支持政策和金融产品。',
                steps: [
                    { t: '主体与架构', d: '境内主体直接出海，还是搭境外主体，税负与合规路径不一样' },
                    { t: '跨境结算与外汇', d: '开立可跨境收付的账户，确认结算币种与购付汇路径' },
                    { t: '数据出境合规', d: '涉及境外客户数据时对照数据出境要求逐项核，拿不准的找专业顾问' },
                    { t: '商标与本地化', d: '目标市场先把商标注册掉，再谈落地推广' },
                ],
                policyTag: '企业出海', finTag: '跨境出海',
                todos: ['确定出海主体架构方案', '找银行确认跨境结算路径', '排查是否涉及数据出境'],
            },
            'app': {
                title: '上架 App', icon: 'phone',
                lead: '依据工信部信管〔2023〕105 号，在境内从事互联网信息服务的 App 主办者要先完成备案，没备案不得提供 App 互联网信息服务。',
                steps: [
                    { t: '软件著作权登记', d: '多数应用商店把软著当上架前置材料' },
                    { t: 'App ICP 备案', d: '通过接入服务商提交，省级通信管理局收到材料后二十个工作日内审核' },
                    { t: '隐私政策与权限说明', d: '收集哪些信息、用在哪里、怎么撤回，都要写清楚并可查' },
                    { t: '应用商店提审', d: '各家商店审核口径不同，驳回原因逐条改再复审' },
                ],
                where: '备案通过接入服务商（云厂商）代提交到省级通信管理局。',
                todos: ['提交软件著作权登记', '找接入服务商提交 App ICP 备案', '写好隐私政策与权限说明'],
            },
            '小程序': {
                title: '上架小程序', icon: 'mini',
                lead: '小程序同样在备案范围内，拿到 ICP 备案号才能上架提供服务。同主体同名称的小程序上架在多个平台，每个平台都要单独备案。',
                steps: [
                    { t: '主体认证', d: '用企业主体做认证，个人主体能开的类目很有限' },
                    { t: '平台侧提交备案', d: '在运行平台提交材料，平台初审后报工信部' },
                    { t: '类目与资质', d: '选定服务类目，按类目补相应经营资质' },
                    { t: '提审发布', d: '备案号下来后提交审核，驳回按平台反馈逐条改' },
                ],
                where: '在小程序运行平台（微信、支付宝、抖音等）的管理后台提交备案，由平台报工信部。',
                todos: ['完成小程序主体认证', '在平台后台提交 ICP 备案', '确认服务类目所需资质'],
            },
            'aigc': {
                title: 'AIGC', icon: 'spark',
                lead: '做生成式 AI 产品，备案是门槛，政策是资源。依《生成式人工智能服务管理暂行办法》，提供具有舆论属性或者社会动员能力的生成式 AI 服务，要通过属地网信部门履行备案或登记程序。',
                steps: [
                    { t: '判断是否落入备案范围', d: '看服务有没有舆论属性或社会动员能力，拿不准先问属地网信部门' },
                    { t: '算法备案', d: '通过互联网信息服务算法备案系统提交' },
                    { t: '生成式 AI 服务备案', d: '经属地网信部门办理备案或登记' },
                    { t: '语料与版权留痕', d: '训练与微调用的数据来源要能说清楚，授权链条留痕' },
                    { t: '显著位置公示', d: '已上线的应用要在显著位置或产品详情页公示所用已备案模型的名称与备案号' },
                ],
                where: '算法备案在互联网信息服务算法备案系统，生成式 AI 服务备案经属地网信部门。',
                policyTag: '人工智能',
                todos: ['判断产品形态是否触发备案义务', '梳理训练语料来源与授权', '把模型名称与备案号加进产品详情页'],
            },
            '自媒体': {
                title: '做自媒体', icon: 'mic',
                lead: '把自媒体当业务做，账号、内容、收入三条线都要合规，接商单之后尤其要注意。',
                steps: [
                    { t: '账号主体认证', d: '用企业主体认证，后续接商单与开票才顺' },
                    { t: '内容合规', d: '涉及资质的领域先拿资质再发内容' },
                    { t: '商单与广告标注', d: '有偿推广要标明广告，代言与效果承诺是高风险区' },
                    { t: '收入申报', d: '平台结算与商单收入按规定入账申报' },
                ],
                todos: ['完成账号企业主体认证', '梳理内容涉及的资质要求', '把商单收入并入正常账务'],
            },
            '合同': {
                title: '写合同', icon: 'file',
                lead: '合同是把口头共识变成能执行的东西。下面四项是最常出问题的地方。',
                steps: [
                    { t: '确认签署主体', d: '对方是公司还是个人、签字人有没有授权，先核清楚' },
                    { t: '必备条款', d: '标的、价款、交付、验收、付款节点、违约责任、争议解决' },
                    { t: '盖章与用印', d: '合同章与公章的效力、骑缝章、电子签的适用范围' },
                    { t: '归档与履约跟踪', d: '签完存档，把付款与交付节点挂进待办' },
                ],
                todos: ['准备一份常用业务的合同模板', '定下用印审批流程', '把在手合同的付款节点录进待办'],
            },
        };
"""
cut("        // ===== 办事详情页 =====", "        let currentTaskKey = '';", NEW_TASK_PAGES + "\n", "办事详情页数据换北京口径")

# renderTaskPage：去掉口径横幅与数据边界，加情况卡与办理入口
cut("        function renderTaskPage(key) {", "        // 一键把办事清单写进看板待办",
"""        function renderTaskPage(key) {
            const d = TASK_PAGES[key];
            let h = `<div class="tp-lead">${d.lead}</div>`;

            // 政府口径要分情况的（交社保），先把情况摆出来
            if (d.cases) {
                h += `<div class="page-section-title">先看你属于哪种情况</div>`;
                h += d.cases.map(c => `<div class="tp-case">
                    <div class="tp-case-t">${c.t}</div>
                    <div class="tp-case-d">${c.d}</div>
                </div>`).join('');
            }

            if (d.parks) {
                h += `<div class="page-section-title">北辰产业云社区四大园区</div>`;
                h += d.parks.map(p => `<div class="tp-park">
                    <div class="tp-park-n">${p.n}</div>
                    <div class="tp-park-d">${p.d}</div>
                </div>`).join('');
            }

            if (d.steps) {
                h += `<div class="page-section-title">办理顺序</div>`;
                h += '<div class="tp-steps">' + d.steps.map((s, i) => `
                    <div class="tp-step">
                        <span class="tp-no">${i + 1}</span>
                        <div><div class="tp-t">${s.t}</div><div class="tp-d">${s.d}</div></div>
                    </div>`).join('') + '</div>';
            }

            if (d.where) h += `<div class="tp-where">在哪办：${d.where}</div>`;

            if (d.todos && d.todos.length) {
                h += `<div class="tp-cta" onclick="taskToPlan('${key}')">${ic('plus', 16)}把这几件事加进我的待办</div>`;
                h += `<div class="tp-note">加进去的是事项本身，时间你自己定。</div>`;
            }

            // 挂上能对得上的政策、金融产品与贴息，点开看官方原文
            if (d.policyTag) {
                const hits = policyPool().filter(p => (p.tags || []).indexOf(d.policyTag) >= 0);
                if (hits.length) {
                    h += `<div class="page-section-title">能对上的政策</div>`;
                    h += hits.slice(0, 8).map(p => policyCard(p, false)).join('');
                    if (hits.length > 8) h += `<div class="pol-count">还有 ${hits.length - 8} 条，去政策页看全部</div>`;
                }
            }
            if (d.finTag) {
                const fh = FIN_PRODUCTS.filter(p => (p.tags || []).indexOf(d.finTag) >= 0);
                if (fh.length) {
                    h += `<div class="page-section-title">能对上的金融产品</div>`;
                    h += fh.map(finCard).join('');
                }
            }
            if (d.subsidyKw) {
                const sh = FIN_SUBSIDIES.filter(s => s.type.indexOf(d.subsidyKw) >= 0);
                if (sh.length) {
                    h += `<div class="page-section-title">可叠加的贴息补贴</div>`;
                    h += sh.map(s => subsidyCard(s, true)).join('');
                }
            }
            return h;
        }

""", "办事详情页渲染重写")

# ============================================================
# 3 管公司经营事项：按政务大厅顺序重排，去掉来源标与折叠区
# ============================================================
def scard(name, icon, desc, onclick):
    return ('                        <div class="service-card" onclick="%s">\\n'
            '                            <span class="sc-icon"><svg class="ic ic-26"><use href="#i-%s"></use></svg></span>\\n'
            '                            <span class="sc-name">%s</span>\\n'
            '                            <span class="sc-desc">%s</span>\\n'
            '                        </div>\\n') % (onclick, icon, name, desc)

BIZ = """                <div class="service-scroll" id="cmBizPane">
                    <div class="page-section-title">常办事项</div>
                    <div class="service-grid">
""" + scard("政策补贴", "doc", "拿你的档案逐条比对政策", "openServiceDetail('政策补贴')") \
    + scard("开公司", "biz", "e 窗通一网通办，一天办结", "openTaskPage('开公司')") \
    + scard("交社保", "shield", "参保登记、公积金、增减员", "openTaskPage('社保')") \
    + scard("报税", "receipt", "税费种认定、三方协议、申报", "openTaskPage('报税')") \
    + scard("开发票", "invoice", "票种核定、UKey、发票申领", "openTaskPage('发票')") \
    + scard("招人用工", "users", "社保就业用工备案统一登记", "openTaskPage('招人')") \
    + """                    </div>
                    <div class="page-section-title">资质与备案</div>
                    <div class="service-grid">
""" + scard("上架 App", "phone", "软著、ICP 备案、商店提审", "openTaskPage('app')") \
    + scard("上架小程序", "mini", "主体认证、平台备案、提审", "openTaskPage('小程序')") \
    + scard("AIGC", "spark", "算法备案、生成式服务备案", "openTaskPage('aigc')") \
    + scard("知识产权", "award", "专利、商标、软著与资助", "openTaskPage('知产')") \
    + scard("出海", "globe", "主体架构、跨境结算、数据", "openTaskPage('出海')") \
    + scard("写合同", "file", "签署主体、必备条款、用印", "openTaskPage('合同')") \
    + scard("做自媒体", "mic", "主体认证、内容合规、商单", "openTaskPage('自媒体')") \
    + """                    </div>
                    <div class="page-section-title">经营支持</div>
                    <div class="service-grid">
""" + scard("融资", "bank", "按适用门槛过筛金融产品", "openServiceDetail('金融服务')") \
    + scard("股权投行", "coin", "股权与投行类产品匹配", "openServiceDetail('融资机会')") \
    + scard("找场地", "pin", "北辰四大园区与载体政策", "openTaskPage('场地')") \
    + scard("行政日历", "calendar", "重要日期与待办管理", "openServiceDetail('行政日历')") \
    + scard("开单诊断", "check", "合规手续全面检查", "openServiceDetail('开单诊断')") \
    + scard("云服务规划", "cloud", "服务器、域名、算力、收款", "openServiceDetail('云服务规划')") \
    + scard("找顾问", "scale", "注册、财会、法务、知产", "openServiceDetail('找顾问')") \
    + """                    </div>
                </div>
"""
cut("""                <div class="service-scroll" id="cmBizPane">""",
    """                <div class="service-scroll" id="riskScroll" style="display:none;"></div>""",
    BIZ, "管公司经营事项重排")

# 折叠区没了，函数一并删
rep("""        // 更多服务：无数据支撑的演示项收在折叠区里，有真数据的顶上去
        function toggleMoreServices() {
            const box = document.getElementById('moreServices');
            const tg = document.getElementById('moreToggle');
            if (!box || !tg) return;
            const open = box.style.display !== 'none';
            box.style.display = open ? 'none' : 'grid';
            tg.classList.toggle('open', !open);
        }
""", "", "删更多服务折叠函数")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第七趟完成")

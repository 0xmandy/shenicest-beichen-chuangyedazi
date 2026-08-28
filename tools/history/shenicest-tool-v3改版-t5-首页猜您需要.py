# -*- coding: utf-8 -*-
"""第五趟：首页改版。删四块、办事入口改「猜您需要」十一项、卡皮巴拉插画、三列布局。
每处锚点命中次数不等于预期就报错退出。"""
import io, sys

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-Claude-2026-08-27.html"
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
# 1. 卡皮巴拉插画：一只基础卡皮巴拉 + 每张卡一个道具
#    单文件零依赖，全部内联 SVG，不引图片链接
# ============================================================
BASE = (
    # 耳朵
    '<ellipse cx="12.6" cy="12.4" rx="3.7" ry="3.3" fill="#8E6540"/>'
    '<ellipse cx="35.4" cy="12.4" rx="3.7" ry="3.3" fill="#8E6540"/>'
    # 头（卡皮巴拉是方头，圆角矩形比椭圆像）
    '<rect x="8.5" y="9" width="31" height="26.5" rx="11.5" ry="12" fill="#B08154"/>'
    # 吻部
    '<ellipse cx="24" cy="28.2" rx="9.2" ry="6.4" fill="#C99C6E"/>'
    # 眼睛
    '<ellipse cx="17.4" cy="20" rx="1.75" ry="2" fill="#3A2A1C"/>'
    '<ellipse cx="30.6" cy="20" rx="1.75" ry="2" fill="#3A2A1C"/>'
    # 鼻子与嘴
    '<ellipse cx="24" cy="25.4" rx="3.5" ry="2.2" fill="#5B4028"/>'
    '<path d="M21.4 30.2 Q24 32.4 26.6 30.2" stroke="#5B4028" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
)

# 道具统一落在右下角 28..47 / 27..47 这块，形状简单、44px 下也认得出
PROPS = {
    # 政策补助：一份文件
    "policy": '<rect x="30" y="28" width="15" height="18" rx="2.2" fill="#FFFFFF" stroke="#8E6540" stroke-width="1.6"/>'
              '<path d="M33.4 33h8.2M33.4 37h8.2M33.4 41h5" stroke="#B08154" stroke-width="1.5" stroke-linecap="round"/>',
    # 融资：钱袋
    "money":  '<path d="M34 30h7l2.6 5.6c1.9 4.1.4 8.4-3.6 9.6a10 10 0 0 1-5 0c-4-1.2-5.5-5.5-3.6-9.6Z" fill="#E8B562" stroke="#B0812F" stroke-width="1.5"/>'
              '<path d="M33.6 30.2 36 27h3l2.4 3.2" fill="none" stroke="#B0812F" stroke-width="1.5" stroke-linejoin="round"/>'
              '<path d="M35.4 36.6 37.5 39.4M39.6 36.6 37.5 39.4M35.6 40h3.8M37.5 39.4V43" stroke="#8A6220" stroke-width="1.3" stroke-linecap="round"/>',
    # 找场地：一栋小楼
    "site":   '<rect x="30" y="28" width="15" height="18" rx="1.8" fill="#E4DCD1" stroke="#8B8073" stroke-width="1.5"/>'
              '<path d="M33.4 32.4h3M39 32.4h3M33.4 36.6h3M39 36.6h3" stroke="#8B8073" stroke-width="1.6" stroke-linecap="round"/>'
              '<rect x="35.4" y="40.6" width="4.2" height="5.4" fill="#8B8073"/>',
    # 交社保：盾牌
    "shield": '<path d="M37.5 27.4 45 30v6.6c0 4.4-3.2 7.4-7.5 9-4.3-1.6-7.5-4.6-7.5-9V30Z" fill="#DCEAF4" stroke="#3E7CA8" stroke-width="1.5" stroke-linejoin="round"/>'
              '<path d="M34.4 36.6 36.8 39l4-4.4" fill="none" stroke="#3E7CA8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    # 开发票：锯齿票据
    "invoice":'<path d="M30 28h15v17l-2.5-1.6-2.5 1.6-2.5-1.6-2.5 1.6L32.5 43 30 44.6Z" fill="#FFFFFF" stroke="#8E6540" stroke-width="1.6" stroke-linejoin="round"/>'
              '<path d="M33.4 33h8.2M33.4 37h5.5" stroke="#D2803F" stroke-width="1.5" stroke-linecap="round"/>',
    # 出海：小船与浪
    "sea":    '<path d="M37.4 26.6v9M37.4 28.4l5.6 2.4-5.6 2.4" fill="none" stroke="#B0812F" stroke-width="1.5" stroke-linejoin="round"/>'
              '<path d="M29.6 36.4h15.8l-2.6 5.2H32.2Z" fill="#E8B562" stroke="#B0812F" stroke-width="1.5" stroke-linejoin="round"/>'
              '<path d="M28.8 44.6c1.6-1.6 3.2-1.6 4.8 0s3.2 1.6 4.8 0 3.2-1.6 4.8 0" fill="none" stroke="#3E7CA8" stroke-width="1.6" stroke-linecap="round"/>',
    # 上架 app：手机
    "app":    '<rect x="31.6" y="27" width="12.4" height="19" rx="2.6" fill="#FFFFFF" stroke="#5B4028" stroke-width="1.6"/>'
              '<path d="M35.4 29.6h4.8" stroke="#5B4028" stroke-width="1.4" stroke-linecap="round"/>'
              '<rect x="34.6" y="33" width="6.4" height="6.4" rx="1.6" fill="#E8B562"/>',
    # 上架小程序：圆角方框加圆点
    "mini":   '<rect x="29.8" y="28.4" width="15.4" height="15.4" rx="4.4" fill="#DCEAF4" stroke="#3E7CA8" stroke-width="1.6"/>'
              '<circle cx="34" cy="36.1" r="1.5" fill="#3E7CA8"/><circle cx="37.5" cy="36.1" r="1.5" fill="#3E7CA8"/>'
              '<circle cx="41" cy="36.1" r="1.5" fill="#3E7CA8"/>',
    # AIGC：星芒
    "spark":  '<path d="M37.4 26.6 39.6 33l6.4 2.2-6.4 2.2-2.2 6.4-2.2-6.4-6.4-2.2 6.4-2.2Z" fill="#E8B562" stroke="#B0812F" stroke-width="1.4" stroke-linejoin="round"/>'
              '<path d="M30.4 27.6v3M31.9 29.1h-3" stroke="#B0812F" stroke-width="1.4" stroke-linecap="round"/>',
    # 做自媒体：话筒
    "mic":    '<rect x="33.8" y="26.6" width="7.4" height="12" rx="3.7" fill="#FFFFFF" stroke="#5B4028" stroke-width="1.6"/>'
              '<path d="M30.4 35.4a7.1 7.1 0 0 0 14.2 0" fill="none" stroke="#5B4028" stroke-width="1.6" stroke-linecap="round"/>'
              '<path d="M37.5 42.6v3.4M34.2 46h6.6" stroke="#5B4028" stroke-width="1.6" stroke-linecap="round"/>',
    # 写合同：纸与笔
    "pen":    '<rect x="28.8" y="29" width="13.6" height="17" rx="2.2" fill="#FFFFFF" stroke="#8E6540" stroke-width="1.6"/>'
              '<path d="M32 34.6h7M32 38.4h4.6" stroke="#B08154" stroke-width="1.5" stroke-linecap="round"/>'
              '<path d="M43.4 26.6a2.3 2.3 0 0 1 3.2 3.2l-8.2 8.2-4.2 1 1-4.2Z" fill="#E8B562" stroke="#B0812F" stroke-width="1.5" stroke-linejoin="round"/>',
}
sprite = ['<svg width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true">',
          '<!-- 猜您需要卡片上的卡皮巴拉：同一只，每张配一个道具。全部内联，无外部图片 -->']
for k, v in PROPS.items():
    sprite.append('<symbol id="capy-%s" viewBox="0 0 48 48">%s%s</symbol>' % (k, BASE, v))
sprite.append('</svg>')
rep("</symbol>\n</svg>\n", "</symbol>\n</svg>\n" + "\n".join(sprite) + "\n", "注入卡皮巴拉雪碧图")

# ============================================================
# 2. 首页：删两张提醒卡、删进度条、改标题、删三个段落
# ============================================================
cut("""                    <div class="alert-card alert-warning" onclick="openServiceDetail('行政日历')">""",
    """                    <div class="board-stats" id="boardStats"></div>""",
    "", "删两张提醒卡与创业进度条")

rep("""                    <div class="task-head">
                        <h3>我要办的事</h3>
                        <span>按你的档案排序</span>
                    </div>""",
    """                    <div class="task-head">
                        <h3>猜您需要</h3>
                        <span>按你的档案排序</span>
                    </div>""", "改标题为猜您需要")

cut("""
                    <div class="section-header">
                        <h3>风险提示</h3>""",
    """
                </div>
            </div>

            <!-- 管公司 Screen""",
    """
""", "删风险提示、推荐机会、近期日程三段")

# ============================================================
# 3. 三列卡片样式
# ============================================================
rep("""        .task-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 0 20px 16px; }
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
        .task-foot { display: flex; align-items: center; }""",
    """        .task-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 9px; padding: 0 20px 16px; }
        .task-card {
            display: flex; flex-direction: column; align-items: center; gap: 3px;
            background: var(--n0); border: var(--hair); border-radius: var(--r-md);
            padding: 11px 5px 10px; cursor: pointer; text-align: center;
            transition: transform .2s cubic-bezier(.25,.46,.45,.94), border-color .2s;
        }
        .task-card:active { transform: scale(.94); border-color: var(--brand-100); }
        .task-card.tk-top { border-color: var(--brand-100); background: linear-gradient(180deg, var(--brand-50), var(--n0) 62%); }
        /* 卡皮巴拉插画：自带填色，不能套 .ic 那套 stroke 规则 */
        .capy { width: 46px; height: 46px; display: block; }
        .task-t { font-size: var(--fs-body); font-weight: 700; color: var(--n900); line-height: 1.3; margin-top: 1px; }
        .task-ev { font-size: 10px; line-height: 1.5; font-weight: 600; color: var(--brand); }
        .task-ev.tk-generic { color: var(--n400); font-weight: 500; }""",
    "三列卡片样式")

# ============================================================
# 4. 入口清单换成十一项，排序跟画像走
# ============================================================
OLD_ENTRIES_START = "        // ===== 首页「我要办的事」入口 ====="
OLD_ENTRIES_END = "        // ===== 办事详情页 ====="
NEW_ENTRIES = """        // ===== 首页「猜您需要」入口 =====
        // 按用户嘴里说得出来的话分类，不按部门分。每条标清背后有没有命题方的真数据。
        const TASK_ENTRIES = [
            { key: '政策',   label: '政策补助',   capy: 'policy' },
            { key: '融资',   label: '融资',       capy: 'money' },
            { key: '场地',   label: '找场地',     capy: 'site' },
            { key: '社保',   label: '交社保',     capy: 'shield' },
            { key: '发票',   label: '开发票',     capy: 'invoice' },
            { key: '出海',   label: '出海',       capy: 'sea' },
            { key: 'app',    label: '上架 App',   capy: 'app' },
            { key: '小程序', label: '上架小程序', capy: 'mini' },
            { key: 'aigc',   label: 'AIGC',       capy: 'spark' },
            { key: '自媒体', label: '做自媒体',   capy: 'mic' },
            { key: '合同',   label: '写合同',     capy: 'pen' },
        ];

        // 库内条数一律现算，不写死
        function policyTagCount(tag) {
            return policyPool().filter(p => (p.tags || []).indexOf(tag) >= 0).length;
        }
        function finTagCount(tag) {
            return FIN_PRODUCTS.filter(p => (p.tags || []).indexOf(tag) >= 0).length;
        }
        function taskEvidence(key) {
            if (key === '政策') return { lib: true, text: '库内 ' + (POLICY_DOCS.length + POLICY_READS.length) + ' 条' };
            if (key === '融资') return { lib: true, text: '库内 ' + (FIN_PRODUCTS.length + FIN_SUBSIDIES.length) + ' 条' };
            if (key === '场地') return { lib: true, text: '库内 ' + policyTagCount('园区载体') + ' 条' };
            if (key === '出海') return { lib: true, text: '库内 ' + (policyTagCount('企业出海') + finTagCount('跨境出海')) + ' 条' };
            if (key === 'aigc') return { lib: true, text: '库内 ' + policyTagCount('人工智能') + ' 条' };
            return { lib: false, text: '通用流程' };
        }

        // 排序跟着画像走：还没注册主体的先看政策、场地、合同；已有主体的先看政策、融资、场地。
        // 做人工智能与机器人的，把 AIGC 提到第三位。
        function taskOrder() {
            const top = state.company === '未注册' ? ['政策', '场地', '合同'] : ['政策', '融资', '场地'];
            if (['人工智能', '智能机器人', '数据要素'].indexOf(state.industry) >= 0) {
                top.splice(2, 0, 'aigc');
                top.length = 3;
            }
            const rest = TASK_ENTRIES.map(t => t.key).filter(k => top.indexOf(k) < 0);
            return top.concat(rest);
        }

        function renderTaskGrid() {
            const box = document.getElementById('taskGrid');
            if (!box) return;
            box.innerHTML = taskOrder().map((k, i) => {
                const t = TASK_ENTRIES.filter(x => x.key === k)[0];
                if (!t) return '';
                const ev = taskEvidence(k);
                return `<div class="task-card${i < 3 ? ' tk-top' : ''}" onclick="taskGo('${t.key}')">
                    <svg class="capy"><use href="#capy-${t.capy}"></use></svg>
                    <div class="task-t">${t.label}</div>
                    <div class="task-ev${ev.lib ? '' : ' tk-generic'}">${ev.text}</div>
                </div>`;
            }).join('');
        }

        function taskGo(key) {
            if (key === '政策') { openServiceDetail('政策补贴'); return; }
            if (key === '融资') { finTab = 'debt'; openServiceDetail('金融服务'); return; }
            openTaskPage(key);
        }

"""
cut(OLD_ENTRIES_START, OLD_ENTRIES_END, NEW_ENTRIES, "入口清单换十一项")

# ============================================================
# 5. 七个新增办事详情页。命题方没给数据的一律通用流程口径，整页零数字。
# ============================================================
NEW_PAGES = """            '发票': {
                title: '开发票', icon: 'receipt', generic: true,
                lead: '能不能开票、能开什么票，决定了你能接什么样的客户。这条线跟税务登记是同一套系统。',
                steps: [
                    { t: '票种核定', d: '按业务类型申请可以开的发票种类与额度' },
                    { t: '领用与开具', d: '通过电子税务局或税控设备领用并开具' },
                    { t: '红冲与作废', d: '开错了按规定红冲，跨期的不能直接作废' },
                    { t: '进销项凭证留存', d: '取得的进项发票与开出的销项发票都要归档备查' },
                ],
                todos: ['确认税务登记状态与办税人员', '申请票种核定', '整理常用开票信息模板'],
            },
            '出海': {
                title: '出海', icon: 'globe',
                lead: '出海要同时过三关：主体与架构、资金进出、数据与内容合规。下面的顺序是通用口径，挂在后面的政策与金融产品才是命题方库里真有的。',
                genericNote: '这四步是通用办事口径，具体材料、时限与费用命题方数据库未覆盖，以受理机关与开户行公告为准。',
                steps: [
                    { t: '主体与架构', d: '境内主体直接出海，还是搭境外主体，税负与合规路径不一样' },
                    { t: '跨境结算与外汇', d: '开立可跨境收付的账户，确认结算币种与购付汇路径' },
                    { t: '数据出境合规', d: '涉及境外客户数据时对照数据出境要求逐项核，判定不了的需人工核' },
                    { t: '商标与本地化', d: '目标市场先把商标注册掉，再谈落地推广' },
                ],
                policyTag: '企业出海', finTag: '跨境出海',
                todos: ['确定出海主体架构方案', '找银行确认跨境结算路径', '排查是否涉及数据出境'],
            },
            'app': {
                title: '上架 App', icon: 'phone', generic: true,
                lead: 'App 上架卡的从来不是技术，是资质与审核材料。下面这几项要在提审之前就备齐。',
                steps: [
                    { t: '软件著作权', d: '登记软著，多数应用商店把它当上架前置' },
                    { t: '备案与资质', d: '按应用类型确认需要哪些前置备案与经营资质' },
                    { t: '隐私政策与权限说明', d: '收集哪些信息、用在哪里、怎么撤回，都要写清楚并可查' },
                    { t: '提审与版本管理', d: '各家商店审核口径不同，驳回原因逐条改再复审' },
                ],
                todos: ['提交软件著作权登记', '写好隐私政策与权限说明', '整理应用商店提审材料'],
            },
            '小程序': {
                title: '上架小程序', icon: 'mini', generic: true,
                lead: '小程序比 App 快，但主体认证与类目资质一样绕不过去。',
                steps: [
                    { t: '主体认证', d: '用企业主体做认证，个人主体能开的类目很有限' },
                    { t: '类目与资质', d: '选定服务类目，按类目补相应经营资质' },
                    { t: '服务条款与隐私', d: '用户协议与隐私政策要在小程序内可查' },
                    { t: '提审与发布', d: '提交审核，驳回后按平台反馈逐条改' },
                ],
                todos: ['完成小程序主体认证', '确认服务类目与所需资质', '准备用户协议与隐私政策'],
            },
            'aigc': {
                title: 'AIGC', icon: 'spark',
                lead: '做生成式 AI 产品，合规与政策是同一件事的两面：备案是门槛，政策库里的支持条目是资源。',
                genericNote: '备案与内容标识属于通用合规口径，是否适用你的产品形态规则判定不了，需人工核。具体材料与时限命题方数据库未覆盖。',
                steps: [
                    { t: '算法备案', d: '具有舆论属性或社会动员能力的算法推荐服务要做备案' },
                    { t: '生成式服务备案', d: '面向公众提供生成式 AI 服务的，按规定完成备案' },
                    { t: '语料与版权', d: '训练与微调用的数据来源要能说清楚，授权链条留痕' },
                    { t: '内容标识', d: '生成内容按要求做标识，人工审核机制要落到流程上' },
                ],
                policyTag: '人工智能',
                todos: ['判断产品形态是否触发备案义务', '梳理训练语料来源与授权', '把内容标识加进产品流程'],
            },
            '自媒体': {
                title: '做自媒体', icon: 'mic', generic: true,
                lead: '把自媒体当业务做，账号、内容、收入三条线都要合规，尤其是接商单之后。',
                steps: [
                    { t: '账号主体认证', d: '用企业主体认证，后续接商单与开票才顺' },
                    { t: '内容合规', d: '涉及资质的领域先拿资质再发内容' },
                    { t: '商单与广告标注', d: '有偿推广要标明广告，代言与效果承诺是高风险区' },
                    { t: '收入申报', d: '平台结算与商单收入按规定入账申报' },
                ],
                todos: ['完成账号企业主体认证', '梳理内容涉及的资质要求', '把商单收入并入正常账务'],
            },
            '合同': {
                title: '写合同', icon: 'file', generic: true,
                lead: '合同不是走形式，是把口头共识变成能执行的东西。下面四项是最常出问题的地方。',
                steps: [
                    { t: '确认签署主体', d: '对方是公司还是个人、签字人有没有授权，先核清楚' },
                    { t: '必备条款', d: '标的、价款、交付、验收、付款节点、违约责任、争议解决' },
                    { t: '盖章与用印', d: '合同章与公章的效力、骑缝章、电子签的适用范围' },
                    { t: '归档与履约跟踪', d: '签完存档，把付款与交付节点挂进待办' },
                ],
                todos: ['准备一份常用业务的合同模板', '定下用印审批流程', '把在手合同的付款节点录进待办'],
            },
"""
rep("            '招人': {", NEW_PAGES + "            '招人': {", "新增七个办事详情页")

# ============================================================
# 6. 首页三张统计卡：被删掉段落的两张改跳对应 tab
# ============================================================
rep("""                    <div class="st-card" onclick="scrollToBoard('bdOppList')">
                        <div class="st-num st-ok">${boardOpps().length}</div><div class="st-label">机会追踪</div>
                    </div>""",
    """                    <div class="st-card" onclick="switchTab('opportunity')">
                        <div class="st-num st-ok">${boardOpps().length}</div><div class="st-label">机会追踪</div>
                    </div>""", "机会统计卡改跳找机会")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第五趟完成")

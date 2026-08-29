# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。

把 44 笔补贴的申请条件里「用四个档案字段就能判」的那部分抽成结构化门槛，写回真理文件。

四个字段：注册地 / 成立年限 / 已有资质 / 从业人数。
判不了的部分不硬判，原样写进 beyond，界面上照实说「这几项要你自己核」。

每条门槛必须能在本地留存的政府原文里找到逐字依据：这里给一个 probe 关键词，
脚本回原文里把包含它的那句整句取出来存成「门槛依据」，probe 找不到就报错停下，
不许手打依据句 —— 手打就等于又回到凭记忆写。

跑法：python3 tools/shenicest-tool-补贴门槛标注.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
SRC = os.path.join(DATA, 'policy-subsidy', 'shenicest-政策补贴条款-结构化-2026-08-29.json')

# reg 取值：朝阳区 / 经开区 / 门头沟区 / 北京市（全市通用，各区都算）
# legal：需要有公司主体，还没注册的直接不符合
# teamOK：明确写了创业团队或未注册个人也能申请
# quals：满足其中一个资质即可
# maxStaff / maxYears：人数与成立年限上限
# probe：回原文取依据句的关键词
# beyond：这四个字段判不了、要用户自己核的部分
G = {
 'CY-AI-01': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。买的必须是遴选出的合作伙伴算力服务，用于大模型训练优化及相关研发'),
 'CY-AI-02': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。要在人工智能生态建设与大模型创新应用里起到关键作用，由专家评审认定'),
 'CY-AI-03': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。要真的建成公共服务平台并投入运营，运营档还要给朝阳区企业低于市价的服务'),
 'CY-AI-04': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。载体形式要是场景实验室、成果转化平台、产业创新中心这一类'),
 'CY-AI-05': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。项目要被认定为引领性、创新性的大模型应用场景，由专家评审定'),
 'CY-AI-06': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。要属于人工智能产业链关键环节的优质创新主体，落地奖励按综合评价给'),
 'CY-AI-07': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。活动必须与朝阳区合作或联合举办'),
 'CY-AI-08': dict(reg=None, legal=False, probe=None,
                   beyond='这份措施原文没写支持对象，注册地和独立法人都没要求到，报之前要看朝阳园管委会当年的实施细则。要入驻与区政府部门共建的产业园区，补贴面积不超过 2000 平方米'),
 'CY-DATA-01': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要真的完成数据产品上架、数据要素登记、数据资产入表或进场交易'),
 'CY-DATA-02': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要首次实现数据合规出境'),
 'CY-DATA-03': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要承接当年发布的重点研发课题并通过揭榜'),
 'CY-DATA-04': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要建设并开放高质量数据集或语料库'),
 'CY-DATA-05': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要做成数据要素×典型应用案例或应用场景建设项目'),
 'CY-DATA-06': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要拿数据资产、数据知识产权或数据托管去融资并产生利息'),
 'CY-DATA-07': dict(reg='朝阳区', legal=True, probe='在朝阳区注册、纳税、纳统',
                    beyond='要主导制定国家、北京市或行业标准'),
 'CY-WEB3-01': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                    beyond='技术方向要落在虚拟现实、数字人、三维渲染引擎、底层工具软件这些指定领域里'),
 'CY-WEB3-02': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                    beyond='要主导制定国家、北京市或行业标准，按起草中发挥的作用综合评定'),
 'CY-WEB3-03': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                    beyond='要向符合条件的第三方平台购买云渲染、云计算或人工智能算力服务'),
 'CY-WEB3-04': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                    beyond='要被认定为引领性、创新性的标杆示范应用场景项目'),
 'CY-WEB3-05': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                    beyond='要被选进高潜企业名单，按技术领先性与企业成长性核定'),
 'CY-MED-01': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                   beyond='要拿到二类或三类医疗器械注册证并在朝阳区产业化，或完成三类器械临床试验'),
 'CY-MED-02': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                   beyond='产品技术性能要处于国内外领先水平并有较高临床价值，由专家评审定'),
 'CY-MED-03': dict(reg='朝阳区', legal=True, probe='在朝阳区规范经营',
                   beyond='要先拿到国家自然科学基金、国家卫健委、市科委或市经信局的相关项目立项'),

 'BJ-LOAN-01': dict(reg='北京市', legal=True, probe='注册在北京市的中小微企业',
                    beyond='要符合国家中小微划型标准；征信报告里中长期与短期借款都为零才算首贷；必须走贷款服务中心的入驻银行'),
 'BJ-VOUCHER-01': dict(reg='北京市', legal=False, teamOK=True, maxStaff=500, probe='职工总数不超过500人',
                       beyond='年销售收入与资产总额各不超过 2 亿元；主营方向要属于新一代信息技术、医药健康、智能制造、人工智能或新材料'),
 'BJ-VOUCHER-02': dict(reg='北京市', legal=True, maxStaff=500, probe='须满足第五条中科技型小微企业之条件',
                       beyond='年销售收入与资产总额各不超过 2 亿元；只能用于租算力做模型或智能体的训练推理'),

 'ZGC-01': dict(reg='北京市', legal=True, maxYears=5, maxStaff=100,
                quals=['国家高新技术企业', '中关村高新技术企业', '科技型中小企业'],
                probe='上一会计年度年末从业人员100人',
                beyond='上年营业收入不超过 2000 万元；最近一个会计年度研发费用同比增量要有 100 万元以上'),
 'ZGC-02': dict(reg='北京市', legal=True, probe='中国创新创业大赛北京赛区',
                beyond='要在中国创新创业大赛北京赛区、中国创新挑战赛北京赛区或中关村国际前沿科技创新大赛拿到规定名次'),
 'ZGC-03': dict(reg='北京市', legal=True, probe='首次成长为国家高新技术企业',
                beyond='要由各区或经开区择优推荐并纳入全市支持清单'),
 'ZGC-04': dict(reg='北京市', legal=True, probe='属于有效期内的北京市新技术新产品',
                beyond='产品要在有效期内的北京市新技术新产品名录里，且属于国际或国内首次研制'),
 'ZGC-05': dict(reg='北京市', legal=True, probe='北京市首台（套）重大技术装备',
                beyond='装备要在有效期内的北京市首台套名录里，并且已投保或续保'),

 'BJ-GJJ-14': dict(reg='北京市', legal=True, probe='具备独立法人资格的信息软件业、制造业、科技服务业企业',
                   beyond='要是新型研发机构，或信息软件业、制造业、科技服务业企业；算力必须租自非关联方'),
 'BJ-GJJ-21': dict(reg='北京市', teamOK=True, legal=False, probe='早期种子、天使轮等早期阶段的潜力企业以及创业团队',
                   beyond='要通过入营培训与公开路演；拿的是拨改投，政府会取得对应转股权利'),
 'BJ-GJJ-22': dict(reg='北京市', legal=True, probe='先进制造业企业一次性奖励',
                   beyond='要是先进制造业企业，且主营业务收入首次达到 2000 万元或 1 亿元'),
 'BJ-GJJ-23': dict(reg='北京市', legal=True,
                   quals=['创新型中小企业', '专精特新中小企业', '专精特新小巨人'],
                   probe='在板的创新型中小企业、专精特新中小企业',
                   beyond='要在北京专精特新专板在板，并已完成合格机构投资者的私募股权融资'),
 'BJ-GJJ-24': dict(reg='北京市', legal=True, probe='支持中小微企业购买使用大模型应用',
                   beyond='要符合中小企业划型标准；买的必须是经评审公告后上架的服务券配券产品'),
 'BJ-GJJ-04': dict(reg='北京市', legal=True, probe='符合本市机器人',
                   beyond='产品要满足机器人十大场景需求、符合本市机器人 1+4 重点产品体系，并在工程化样机阶段首试首用'),
 'BJ-OPC-01': dict(reg='北京市', legal=True, probe='为入驻OPC企业发放',
                   beyond='要入驻 OPC 成长社区；资源包由社区按季度统一申请兑付'),
 'BJ-OPC-02': dict(reg='北京市', teamOK=True, legal=False, probe='由OPC社区推荐OPC企业参赛',
                   beyond='要由 OPC 社区推荐参赛，并通过路演或在专项赛道被评为优质项目'),
 'BJ-ZJTX-STD': dict(reg='北京市', legal=True, quals=['创新型中小企业'],
                     probe='已获得科技和创新型中小企业称号',
                     beyond='还要看上年营收、近两年研发费用与占比、I 类知识产权、细分市场占有率、专精特新评价得分五项'),

 'BDA-01': dict(reg='经开区', legal=True, probe='在亦庄新城225平方公里范围内实际经营',
                beyond='模型服务要经中央网信办备案；与模型服务方须为非关联企业'),
 'BDA-02': dict(reg='经开区', legal=True, probe='在亦庄新城225平方公里范围内依法实际经营',
                beyond='要是规上工业、信息传输软件、科研技术服务企业或国家级小巨人；研发费用同比要增长超过 10%'),

 'MTG-01': dict(reg='门头沟区', legal=True, probe='首次认定北京市“创新型”中小企业称号',
                beyond='要首次获得三档资质之一；企业要落在人工智能、超高清数字视听或心血管创新药械三大领域'),
 'MTG-02': dict(reg='门头沟区', legal=True, quals=['专精特新中小企业', '专精特新小巨人'],
                probe='“专精特新”小微企业经营性贷款实际发生利息',
                beyond='要有实际发生利息的经营性贷款；能不能兑现看上级资金拨付情况'),
}

SENT = re.compile(r'[^。；;\n]{0,120}')


def evidence(body, probe):
    """回原文取包含 probe 的那一句，逐字返回。取不到返回 None。"""
    i = body.find(probe)
    if i < 0:
        return None
    start = max(body.rfind('。', 0, i), body.rfind('\n', 0, i), body.rfind('；', 0, i)) + 1
    end = min([x for x in (body.find('。', i), body.find('\n', i), body.find('；', i)) if x > 0]
              or [i + len(probe)])
    return body[start:end + 1].strip()


def main():
    d = json.load(io.open(SRC, encoding='utf-8'))
    miss = [x['id'] for x in d['条款'] if x['id'] not in G]
    if miss:
        raise SystemExit('这几条没写门槛：%s' % miss)

    bad = []
    for it in d['条款']:
        g = dict(G[it['id']])
        probe = g.pop('probe')
        ev = None
        if probe:
            path = os.path.join(DATA, it['来源']['本地文件'])
            body = io.open(path, encoding='utf-8').read()
            ev = evidence(body, probe)
            if not ev:
                bad.append((it['id'], probe, it['来源']['本地文件']))
                continue
        it['判定门槛'] = {
            'reg': g.get('reg'),
            'legal': bool(g.get('legal')),
            'teamOK': bool(g.get('teamOK')),
            'quals': g.get('quals') or [],
            'maxStaff': g.get('maxStaff'),
            'maxYears': g.get('maxYears'),
            'beyond': g['beyond'],
        }
        it['门槛依据'] = ev

    if bad:
        print('这几条的 probe 在原文里找不到，先修 probe 再跑：')
        for i, p, f in bad:
            print('  %-14s %-30s %s' % (i, p, f))
        return 1

    d['判定门槛口径'] = ('只用四个档案字段能判的那部分：注册地、成立年限、已有资质、从业人数。'
                   '判不了的写进 beyond，界面照实说要用户自己核，不硬判。'
                   '门槛依据是从本地原文里整句取的，不许手打。')
    json.dump(d, io.open(SRC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    import collections
    print('44 条门槛已标注')
    print('注册地要求：', dict(collections.Counter(x['判定门槛']['reg'] for x in d['条款'])))
    print('要资质的：', sum(1 for x in d['条款'] if x['判定门槛']['quals']))
    print('收创业团队的：', sum(1 for x in d['条款'] if x['判定门槛']['teamOK']))
    print('有人数上限的：', sum(1 for x in d['条款'] if x['判定门槛']['maxStaff']))
    return 0


if __name__ == '__main__':
    sys.exit(main())

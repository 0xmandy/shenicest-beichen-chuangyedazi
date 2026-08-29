# -*- coding: utf-8 -*-
"""由 Claude 生成，属于 shenicest 黑客松北辰命题原型「创业搭子」。

把结构化的补贴条款 JSON 渲染成给人读的简洁版 Markdown。
读者读完这一份就知道自己能不能申请、能拿多少、什么时候截止，不用再去翻原文。
每条末尾保留官方链接，想核实的人点得回去。

改内容改 JSON，不要改这里生成的 md —— md 每次重跑都会被覆盖。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'data', 'policy-subsidy', 'shenicest-政策补贴条款-结构化-Claude-2026-08-29.json')
OUT = os.path.join(HERE, '..', 'data', 'policy-subsidy', 'shenicest-政策补贴条款-简洁版-Claude-2026-08-29.md')

LEVEL_ORDER = ['朝阳区', '北京市', '中关村', '经开区', '门头沟区']


def money_line(r):
    parts = []
    if r.get('比例'):
        parts.append('按比例：' + r['比例'])
    if r.get('单笔上限'):
        parts.append('单笔／单项：' + r['单笔上限'])
    if r.get('年度上限'):
        parts.append('每年封顶：' + r['年度上限'])
    if r.get('累计上限'):
        parts.append('累计封顶：' + r['累计上限'])
    return '；'.join(parts) or '原文未写具体金额'


def main():
    data = json.load(open(SRC, encoding='utf-8'))
    items = data['条款']
    lines = []
    a = lines.append

    a('# 北京与朝阳补贴政策简洁版（%d 条可申请的钱）' % len(items))
    a('')
    a('本文件由 Claude 生成，属于 shenicest 黑客松北辰命题参赛项目「创业搭子」。')
    a('')
    a('一条 = 一笔能单独申请的钱。金额和条件逐字来自政府网站上的政策原文，'
      '本地留了原文副本，每条都能点回官方页面核对。原文没写的（比如没写申报时间的），'
      '这里写「原文未写」，不替它补。')
    a('')
    a('抓取日 %s。政策会改、会过期，真要申报之前按链接再核一次。' % data['抓取日'])
    a('')

    # 目录
    a('## 先看这张表')
    a('')
    a('| 编号 | 补贴项 | 谁发的 | 最多能拿 | 什么时候截止 |')
    a('|---|---|---|---|---|')
    for it in sorted(items, key=lambda x: (LEVEL_ORDER.index(x['层级']) if x['层级'] in LEVEL_ORDER else 9, x['id'])):
        rng = it['补贴金额范围']
        cap = rng.get('年度上限') or rng.get('单笔上限') or rng.get('累计上限') or rng.get('比例') or '原文未写'
        cap = cap.split('；')[0]
        when = it['申报时间'].split('；')[0]
        # 表格只放能一眼看完的短句，展开在下面的分条里
        if when.startswith('原文未写'):
            when = '原文未写，看每年的实施细则'
        elif len(when) > 26:
            when = when[:24] + '…'
        a('| %s | %s | %s | %s | %s |' % (it['id'], it['补贴项'], it['层级'], cap, when))
    a('')

    for lv in LEVEL_ORDER:
        group = [x for x in items if x['层级'] == lv]
        if not group:
            continue
        a('---')
        a('')
        a('## %s（%d 条）' % (lv, len(group)))
        a('')
        for it in sorted(group, key=lambda x: x['id']):
            a('### %s　%s' % (it['id'], it['补贴项']))
            a('')
            a(it['一句话'])
            a('')
            a('- 能拿多少：%s' % money_line(it['补贴金额范围']))
            a('- 谁能申请：')
            for c in it['申请条件']:
                a('  - %s' % c)
            a('- 怎么给：%s' % it['兑付方式'])
            a('- 什么时候：%s' % it['申报时间'])
            a('- 能不能和别的一起拿：%s' % it['叠加规则'])
            a('- 出自：《%s》%s' % (it['政策名称'], it['条款']))
            a('- 金额原话：%s' % it['金额原文'])
            a('- 条件原话：%s' % it['条件原文'])
            a('- 官方链接：%s' % it['来源']['url'])
            a('')

    a('---')
    a('')
    a('## 待核验缺口')
    a('')
    a('这几件事这一版没做到，写在这里划清结论的边界。')
    a('')
    a('- 命题方原文库那 86 个文件名里，本轮只联网补齐了 30 份，其余按标题判断多为行动计划与规划类，'
      '或没找到可靠的官方全文；朝阳区小微企业融资风险补偿方案、朝阳区专利资助及奖励暂行办法这两份抓取失败。')
    a('- 朝阳区产业政策申报平台 cycyzj.bjchy.gov.cn 本轮返回 504，'
      '各条款的年度实施细则与申报截止日拿不到，所以朝阳区那批条款的申报时间统一写「原文未写」。')
    a('- 政策时效未逐条核对。朝阳区互联网3.0、通用人工智能两份措施发布于 2023 与 2024 年，'
      '数字医疗措施原文写明有效期五年，其余多数没写废止日。')
    a('- 金额档次里凡是原文写「根据项目成效」「综合评价结果」的，实际能拿到多少由评审定，'
      '这里只照抄上限，不做任何折算或估算。')
    a('')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('写出', OUT)
    print('条款', len(items), '字数', sum(len(x) for x in lines))


if __name__ == '__main__':
    main()

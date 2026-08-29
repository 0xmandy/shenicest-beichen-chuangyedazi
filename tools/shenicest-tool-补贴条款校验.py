# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。

补贴条款结构化结果的数字防火墙。三道校验，任何一道不过就打 MISMATCH：

1. 引文校验：每条记录的「金额原文」「条件原文」必须逐字出现在它声明的本地原文文件里
   （只归一化空白与全半角标点，不做同义改写）。
2. 数字校验：「补贴金额范围」里出现的每一个「N万元/N亿元/N%」，必须能在同一份原文里找到。
   这一条防的是把 500 万看成 5000 万这种最致命的错。
3. 文件校验：来源文件必须存在。

退出码非 0 就是有条款没过，别把结果往界面上接。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'data', 'policy-subsidy', 'shenicest-政策补贴条款-结构化-2026-08-29.json')

# 政府网页里同一个字符可能是全角也可能是半角，归一化后再比，
# 但数字本身不做任何变换 —— 数字是这套校验要守的东西。
TRANS = str.maketrans({
    '（': '(', '）': ')', '，': ',', '。': '.', '；': ';', '：': ':',
    '“': '"', '”': '"', '‘': "'", '’': "'", '％': '%', '　': ' ',
    '〔': '[', '〕': ']', '＋': '+', '－': '-', '—': '-', '－': '-',
})


def norm(s):
    s = s.translate(TRANS)
    s = re.sub(r'[\s​ ؏‏‪-‮]+', '', s)
    return s


NUM_PAT = re.compile(r'\d+(?:\.\d+)?\s*(?:万元|亿元|%)')


def main():
    data = json.load(open(SRC, encoding='utf-8'))
    items = data['条款']
    cache = {}
    fails, checked = [], 0

    for it in items:
        pid = it['id']
        rel = it['来源']['本地文件']
        path = os.path.join(HERE, '..', 'data', rel)
        if not os.path.exists(path):
            fails.append((pid, '来源文件', '文件不存在: ' + rel))
            continue
        if path not in cache:
            cache[path] = norm(open(path, encoding='utf-8').read())
        body = cache[path]

        for field in ('金额原文', '条件原文'):
            quote = it.get(field) or ''
            if not quote:
                fails.append((pid, field, '空引文'))
                continue
            checked += 1
            if norm(quote) not in body:
                fails.append((pid, field, '引文在原文里找不到: ' + quote[:46]))

        rng = it.get('补贴金额范围') or {}
        blob = norm(' '.join(str(v) for v in rng.values() if v))
        for num in NUM_PAT.findall(blob):
            checked += 1
            n = norm(num)
            if n not in norm(it.get('金额原文', '')) and n not in body:
                fails.append((pid, '补贴金额范围', '数字在原文里找不到: ' + num))

        # 排序值是「一家企业最多能拿到手多少钱」，标 quoted 的必须能在金额原话里找到。
        # 标 derived 的是算出来的（比如贴息按放款额百分比折出来），必须写明怎么算的。
        src = it.get('金额排序值来源')
        cap = it.get('金额排序值万元')
        if src is None or cap is None:
            fails.append((pid, '金额排序值', '缺 金额排序值万元 或 金额排序值来源'))
        elif src == 'quoted':
            checked += 1
            money = norm(it.get('金额原文', ''))
            want = ('%g万元' % (cap / 10000.0)) if cap >= 10000 and cap % 10000 == 0 else '%d万元' % cap
            alt = '%g亿元' % (cap / 10000.0)
            if norm(want) not in money and norm(alt) not in money:
                fails.append((pid, '金额排序值', '%d万 在金额原话里找不到（%s / %s）' % (cap, want, alt)))
        elif src in ('derived', 'na'):
            checked += 1
            if not it.get('金额排序值说明'):
                fails.append((pid, '金额排序值', '标了 %s 却没写怎么来的' % src))
        else:
            fails.append((pid, '金额排序值', '来源只能是 quoted / derived / na，实际是 ' + str(src)))

        # 门槛依据必须逐字来自原文。没有可判门槛的条目允许为空，但那样 reg/quals/人数/年限
        # 必须全是空的 —— 有门槛却没依据，就是凭空判人。
        gate = it.get('判定门槛')
        if gate is None:
            fails.append((pid, '判定门槛', '缺 判定门槛'))
        else:
            hard = bool(gate.get('reg') or gate.get('quals') or gate.get('maxStaff')
                        or gate.get('maxYears') or gate.get('legal'))
            ev = it.get('门槛依据')
            if hard and not ev:
                fails.append((pid, '门槛依据', '设了门槛却没有原文依据'))
            elif ev:
                checked += 1
                if norm(ev) not in body:
                    fails.append((pid, '门槛依据', '依据句在原文里找不到: ' + ev[:40]))
            if not gate.get('beyond'):
                fails.append((pid, '判定门槛', 'beyond 不能空，判不了的部分要写出来'))

        # 卡面那一格和排序值必须是同一个数，两边分开写就会有一天对不上
        txt = it.get('卡面金额')
        if not txt:
            fails.append((pid, '卡面金额', '缺 卡面金额'))
        elif cap:
            checked += 1
            wan = 0
            for n, u in re.findall(r'(\d+(?:\.\d+)?)\s*(万|亿)', txt):
                wan = max(wan, float(n) * (10000 if u == '亿' else 1))
            if int(wan) != cap:
                fails.append((pid, '卡面金额', '卡面写 %s，排序值是 %d万，对不上' % (txt, cap)))

    print('条款 %d 条，校验点 %d 个' % (len(items), checked))
    if not fails:
        print('全部 MATCH')
        return 0
    print('MISMATCH %d 处：' % len(fails))
    for pid, field, msg in fails:
        print('  %-14s %-12s %s' % (pid, field, msg))
    return 1


if __name__ == '__main__':
    sys.exit(main())

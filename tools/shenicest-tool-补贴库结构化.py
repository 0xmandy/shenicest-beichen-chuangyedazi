# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。
把补贴条款真理文件压成前端可用的 JS 数据块，和政策库、金融库两个脚本同一个做法。

真理文件是 data/policy-subsidy/shenicest-政策补贴条款-结构化-2026-08-29.json，
里面每个金额和条件都能回链到 data/policy-raw/ 下留存的政府原文。
改内容改那份 JSON，跑一遍 data/shenicest-tool-补贴条款校验.py 过了，再跑这个脚本。

这里只做搬运和改名，不派生任何金额与条件 —— 派生就是幻觉。
唯一的计算是把申报窗口跟今天比一下算出「还能不能报」，那个放在前端做，
因为 demo 什么时候被打开是不确定的，编译期算死了会过期。
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('SUBSIDY_JSON') or os.path.join(
    HERE, '..', 'data', 'policy-subsidy', 'shenicest-政策补贴条款-结构化-2026-08-29.json')
CHECK = os.path.join(HERE, 'shenicest-tool-补贴条款校验.py')
OUT = os.environ.get('SUBSIDY_OUT') or os.path.join(HERE, 'subsidy-db.js')

if not os.path.exists(SRC):
    raise SystemExit('找不到补贴条款真理文件：%s' % SRC)

# 先过校验再出数据。校验不过就别往 html 里塞，这是这个项目的立身之本。
if os.path.exists(CHECK):
    r = subprocess.run([sys.executable, CHECK], capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        raise SystemExit('补贴条款校验没过，不出数据块')

data = json.load(open(SRC, encoding='utf-8'))
items = data['条款']

# 主题沿用政策库那 18 类标签词表，匹配引擎两边共用一套词，不另起炉灶
out = []
for it in items:
    rng = it['补贴金额范围']
    out.append({
        'id': it['id'],
        'name': it['补贴项'],
        'policy': it['政策名称'],
        'clause': it['条款'],
        'level': it['层级'],
        'tag': it['主题'],
        'one': it['一句话'],
        'ratio': rng.get('比例') or '',
        'once': rng.get('单笔上限') or '',
        'year': rng.get('年度上限') or '',
        'total': rng.get('累计上限') or '',
        'capWan': it['金额排序值万元'],
        'capText': it['卡面金额'],
        'conds': it['申请条件'],
        'pay': it['兑付方式'],
        'stack': it['叠加规则'],
        'when': it['申报时间'],
        'win': it['申报窗口'],
        'moneyQuote': it['金额原文'],
        'condQuote': it['条件原文'],
        'gate': it['判定门槛'],
        'gateFrom': it.get('门槛依据') or '',
        # 年度细则：措施是纲领，年度实施方案才决定当年实际开哪几个方向。
        # 只有走年度制的朝阳区那 23 条有这个字段，其余的没有，前端要判 undefined。
        'plan': it.get('年度细则'),
        'url': it['来源']['url'],
    })

body = (
    "        // ===== 补贴条款库（44 笔企业能单独申请的钱）=====\n"
    "        // 来源：政府网站政策原文，本地留存在 data/policy-raw/，逐条可回链。\n"
    "        // 由 tools/shenicest-tool-补贴库结构化.py 从真理文件生成，改内容改真理文件不要改这里。\n"
    "        // capWan = 一家企业按这一条最多能拿到手多少钱（万元），手工设定只用于排序，不许用正则覆盖。\n"
    "        // win.st = dated 有明确截止日 / rolling 常年可报 / unknown 原文没写批次。\n"
    "        // plan = 年度细则里有没有这一条。listed 当年列了 / notlisted 当年没列、报不了。\n"
    "        // 只有走年度制的朝阳区那 23 条有 plan，其余条目 plan 为 null，判的时候别忘了。\n"
    "        const SUBSIDY_ITEMS = %s;\n"
) % json.dumps(out, ensure_ascii=False, separators=(',', ':'))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(body)

import collections
print('补贴条款', len(out), '条')
print('层级分布', dict(collections.Counter(x['level'] for x in out)))
print('主题分布', dict(collections.Counter(x['tag'] for x in out)))
print('申报窗口', dict(collections.Counter(x['win']['st'] for x in out)))
print('输出', OUT, os.path.getsize(OUT), 'bytes')

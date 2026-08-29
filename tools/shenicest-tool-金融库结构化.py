# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型。
把《朝阳数据要素产业园金融工具统计_20260821.xlsx》结构化成前端数据。
机构、产品名、额度、期限、利率、门槛、特点、补充说明一律原文照抄，一个字不改写。
只额外派生 tags（给匹配用）和 rateKnown/amountKnown（标记原表是不是写「根据企业实际情况不定」）。"""
import glob, json, os, re

import openpyxl

# 源表不进 repo（是命题给的原始材料，从 金融资料.zip 里解出统计表）。
# 跑之前把 xlsx 放到 data/ 下，或者用 FINANCE_XLSX 指过来。
_HERE = os.path.dirname(os.path.abspath(__file__))
_cand = [os.environ['FINANCE_XLSX']] if os.environ.get('FINANCE_XLSX') else \
    sorted(glob.glob(os.path.join(_HERE, '..', 'data', '*金融工具统计*.xlsx')))
if not _cand or not os.path.exists(_cand[0]):
    raise SystemExit('找不到金融库源表。把 朝阳数据要素产业园金融工具统计_*.xlsx 放到 data/ 下，'
                     '或者 FINANCE_XLSX=/path/to.xlsx 再跑')
SRC = _cand[0]
OUT = os.environ.get('FINANCE_OUT') or os.path.join(_HERE, 'finance-db.js')

TAG_RULES = [
    ('数据要素', ['数据资产', '数据要素', '北数所', '数据易贷', '入表', '数据交易', '朝数贷']),
    ('知识产权', ['知识产权', '专利', '商标', '软著']),
    ('专精特新', ['专精特新', '小巨人']),
    ('科技型', ['科技', '科创', '高新', '研发', '技术企业']),
    ('纯信用', ['纯信用', '无需担保', '免担保', '信用贷', '无抵押']),
    ('要抵押', ['抵押', '质押', '不动产', '抵质押']),
    ('供应链', ['供应链', '应收', '票据', '保理', '订单', '核心企业']),
    ('跨境出海', ['跨境', '外汇', '结汇', '汇率', '境外', '出海', 'FT', '离岸']),
    ('股权投资', ['股权', '投贷联动', '基金', '上市', 'IPO', '并购', '定增', '做市', '投行']),
    ('政策贴息', ['贴息', '补贴', '担保费', '财政']),
    ('初创期', ['初创', '成立不满', '新设', '早期', '初创期']),
    ('现金管理', ['理财', '存款', '现金管理', '结算', '交易银行', '账户']),
    ('个人金融', ['个人', '法人', '高管', '员工', '财富管理']),
]

# 债权类进「贷款融资」，其余进「股权与投行」
DEBT_TYPES = ['债权', '债权（投贷联动）', '投行（债权）', '交易银行', '数字场景金融', '个人金融（信用贷）', '个人金融（经营贷）']

UNKNOWN = ['根据企业实际情况不定', '不定', '以实际', '面议']


def clean(v):
    if v is None:
        return ''
    s = str(v).strip()
    return re.sub(r'\s+', ' ', s)


def known(v):
    return bool(v) and not any(u in v for u in UNKNOWN)


def pick_tags(blob):
    tags = [t for t, kws in TAG_RULES if any(k in blob for k in kws)]
    return tags[:4] or ['通用融资']


wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(min_row=1, values_only=True))

appendix_at = None
for i, r in enumerate(rows):
    if r[2] and '附表' in str(r[2]):
        appendix_at = i
        break

products = []
for r in rows[4:appendix_at]:
    name = clean(r[3])
    org = clean(r[2])
    if not name or not org or org == '序号':
        continue
    amount, term, rate = clean(r[7]), clean(r[8]), clean(r[9])
    blob = ' '.join([name, clean(r[4]), clean(r[5]), clean(r[6]), clean(r[10])])
    products.append({
        'id': 'F%03d' % (len(products) + 1),
        'org': org,
        'name': name,
        'type': clean(r[4]),
        'threshold': clean(r[5]),
        'feature': clean(r[6]),
        'amount': amount,
        'term': term,
        'rate': rate,
        'note': clean(r[10]),
        'debt': clean(r[4]) in DEBT_TYPES,
        'amountKnown': known(amount),
        'rateKnown': known(rate),
        'tags': pick_tags(blob),
    })

subsidies = []
for r in rows[appendix_at:]:
    no = clean(r[2])
    if not no.isdigit():
        continue
    subsidies.append({
        'id': 'S%02d' % (len(subsidies) + 1),
        'type': clean(r[3]),
        'scope': clean(r[4]),
        'content': clean(r[5]),
        'provider': clean(r[6]),
        'tags': pick_tags(' '.join([clean(r[3]), clean(r[4]), clean(r[5])])),
    })

body = (
    "        // ===== 金融库（来源：命题方《朝阳数据要素产业园金融工具统计_20260821.xlsx》）=====\n"
    "        // 产品 %d 条 + 可叠加的金融类政策 %d 条。机构、产品名、额度、期限、利率、门槛全部原文照抄。\n"
    "        // amountKnown / rateKnown = 原表这一格是不是写了「根据企业实际情况不定」，界面据此显示「以机构核定为准」。\n"
    "        const FIN_PRODUCTS = %s;\n\n"
    "        const FIN_SUBSIDIES = %s;\n"
) % (
    len(products), len(subsidies),
    json.dumps(products, ensure_ascii=False),
    json.dumps(subsidies, ensure_ascii=False),
)

open(OUT, 'w', encoding='utf-8').write(body)

print('产品', len(products), '金融类政策', len(subsidies))
orgs = {}
for p in products:
    orgs[p['org']] = orgs.get(p['org'], 0) + 1
print('机构分布', orgs)
print('债权类', sum(1 for p in products if p['debt']), '股权投行类', sum(1 for p in products if not p['debt']))
print('额度写了具体数字的', sum(1 for p in products if p['amountKnown']), '/', len(products))
print('利率写了具体口径的', sum(1 for p in products if p['rateKnown']), '/', len(products))
tc = {}
for p in products:
    for t in p['tags']:
        tc[t] = tc.get(t, 0) + 1
print('标签', dict(sorted(tc.items(), key=lambda x: -x[1])))
print('输出', OUT, os.path.getsize(OUT), 'bytes')

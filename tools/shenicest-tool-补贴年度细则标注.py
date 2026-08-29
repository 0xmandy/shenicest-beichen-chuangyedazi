# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。

干什么：给朝阳区那 23 条补贴标上「2026 年度细则里有没有这一条」。

为什么要有这一步：措施是纲领，写的是这条钱最多能给多少；每年另发的实施方案
才决定当年实际开哪几个方向。两者不是一回事——朝阳区通用人工智能措施写了
八条能拿的钱，2026 年度实施方案只列了其中两条，剩下六条今年根本报不了。
界面上原来这 23 条一律显示「看年度细则」，等于把「今年能报」和「今年没开」
混在一起，用户照着去报会白跑。

怎么定：映射是手写的（下面 MAP），但每一条都要过机器核验才允许落盘：
  listed    这条的金额原文里的数字，必须全部出现在对应方向的支持内容里
  notlisted 不许有任何一个方向同时满足两件事：数字被完整覆盖，且支持内容里
            出现了这条金额原文里一段十个字以上的原话

反向核验为什么要两个信号一起看：只比数字会大面积误报。500 万、200 万这种
金额在好几个方向里都出现，光看数字会把「创新服务载体建设」判成跟「加强算力
资源保障」是同一条。只比原话又会漏：年度方案是照措施改写的，措施写「补贴」
方案写「支持」，一改措辞长短语就断了。两个都命中才算真冲突。

方向名、支持内容、申报截止日全部从本地留档的年度方案与通知里取，不手打。
核验不过就非 0 退出，不写文件。

输入：data/policy-raw/rules/ 下四份年度征集通知与它们的实施方案附件
输出：就地改写补贴条款真理文件，给命中的条目加 年度细则 字段

用法：python3 tools/shenicest-tool-补贴年度细则标注.py
跑完接着跑 补贴条款校验.py 与 补贴库结构化.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
RULES = os.path.join(ROOT, 'data', 'policy-raw', 'rules')
TRUTH = os.path.join(ROOT, 'data', 'policy-subsidy',
                     'shenicest-政策补贴条款-结构化-2026-08-29.json')
YEAR = '2026'

# 四份政策各自的年度征集通知与实施方案附件。id 是抓取脚本按页面 hash 派生的。
FAM = {
    'CY-AI':   {'notice': 'RULE-CHY-63739e25a2', 'plan': 'RULE-CHY-63739e25a2-a1'},
    'CY-DATA': {'notice': 'RULE-CHY-665e5225bb', 'plan': 'RULE-CHY-665e5225bb-a1'},
    'CY-WEB3': {'notice': 'RULE-CHY-5bc9082561', 'plan': 'RULE-CHY-5bc9082561-a1'},
    'CY-MED':  {'notice': 'RULE-CHY-0cc13434de', 'plan': 'RULE-CHY-0cc13434de-a1'},
}

# 条款 -> 2026 年度方向编号。None 表示年度方案里没有这一条。
# 第三项是容差：明知会缺、且已经查清原因的数字，写清原因才允许放行，不许空着放行。
MAP = {
    'CY-AI-01': ('2026-01', '',
                 {('30', '%'): '措施写区内 50%、区外 30% 两档，2026 年度方案只列了区内 50% 这一档'}),
    'CY-AI-02': (None, '', {}),
    'CY-AI-03': (None, '', {}),
    'CY-AI-04': (None, '', {}),
    'CY-AI-05': ('2026-06a', '措施第六条被年度方案拆成两个方向，本条对应场景那半',
                 {('200', '万元'): '第六条后半「优秀垂直领域模型」被拆成方向 2024-06b，200 万在那一条里'}),
    'CY-AI-06': (None, '', {}),
    'CY-AI-07': (None, '', {}),
    'CY-AI-08': (None, '', {}),
    'CY-DATA-01': (None, '', {}),
    'CY-DATA-02': ('2026-08', '', {}),
    'CY-DATA-03': ('2026-12', '', {}),
    'CY-DATA-04': ('2026-13', '', {}),
    'CY-DATA-05': (None, '', {}),
    'CY-DATA-06': ('2026-15', '', {}),
    'CY-DATA-07': ('2026-16', '', {}),
    'CY-WEB3-01': ('2026-02', '', {}),
    'CY-WEB3-02': ('2026-03', '', {}),
    'CY-WEB3-03': (None, '', {}),
    'CY-WEB3-04': ('2026-06a', '年度方案另有 2026-06b 支持示范解决方案打造，本条对应场景那半', {}),
    'CY-WEB3-05': ('2026-07', '', {}),
    'CY-MED-01': ('2026-03a', '', {}),
    'CY-MED-02': ('2026-02', '', {}),
    'CY-MED-03': ('2026-07', '', {}),
}

NUM = re.compile(r'(\d+(?:\.\d+)?)\s*(万元|亿元|%|％)')
ROW = re.compile(r'^(20\d\d-[0-9a-z]+)\s*\|\s*([^|]{2,40})\|')
DEADLINE = re.compile(r'即日起至\s*(20\d\d年\d{1,2}月\d{1,2}日)\s*申报')
# 金额原文里带数字的片段，用来做原话比对
PHRASE = re.compile(r'[^。；]{0,30}?\d+(?:\.\d+)?\s*(?:万元|亿元|%|％)[^。；]{0,30}')


def flat(s):
    """比原话时把空白与标点抹掉，措辞里的顿号括号不该影响判断。"""
    return re.sub(r'\s|[，。、；：（）()「」“”"\']', '', s or '')


def read(name):
    p = os.path.join(RULES, name + '.txt')
    if not os.path.exists(p):
        sys.exit('缺语料：%s。先跑 shenicest-tool-年度申报细则抓取.py' % p)
    return io.open(p, encoding='utf-8').read()


def nums(s):
    return set((a, b.replace('％', '%')) for a, b in NUM.findall(s or ''))


def load_dirs(fam):
    """从实施方案里抽 编号 -> (方向名, 支持内容)。"""
    out = {}
    for ln in read(FAM[fam]['plan']).split('\n'):
        m = ROW.match(ln)
        if m:
            cols = [c.strip() for c in ln.split('|')]
            out[m.group(1)] = (m.group(2).strip(), cols[4] if len(cols) > 4 else '')
    if not out:
        sys.exit('实施方案里一个方向都没抽到：%s' % fam)
    return out


def load_deadline(fam):
    m = DEADLINE.search(read(FAM[fam]['notice']))
    return m.group(1) if m else None


def main():
    dirs = {f: load_dirs(f) for f in FAM}
    dead = {f: load_deadline(f) for f in FAM}
    for f in FAM:
        print('%-9s 方向 %d 个，申报截止 %s'
              % (f, len(dirs[f]), dead[f] or '原文未写'))
    print()

    data = json.load(io.open(TRUTH, encoding='utf-8'))
    items = {x['id']: x for x in data['条款']}
    bad, listed, notlisted = 0, 0, 0

    for sid, (code, note, tol) in MAP.items():
        if sid not in items:
            print('FAIL  %s 不在真理文件里' % sid)
            bad += 1
            continue
        s = items[sid]
        fam = sid.rsplit('-', 1)[0]
        want = nums(s['金额原文'])

        if code is None:
            # 反向核验：数字被完整覆盖，且支持内容里有这条的一段原话，两个都中才算冲突
            phr = [p for p in PHRASE.findall(s['金额原文'] or '') if len(flat(p)) >= 10]
            leak = []
            for c, (_, ct) in dirs[fam].items():
                if not (want and want <= nums(ct)):
                    continue
                if any(flat(p) in flat(ct) for p in phr):
                    leak.append(c)
            if leak:
                print('FAIL  %-13s 标了 notlisted，但方向 %s 的金额与原话都对得上'
                      % (sid, ','.join(leak)))
                bad += 1
                continue
            s['年度细则'] = {
                '年度': YEAR, 'st': 'notlisted', '方向编号': None, '方向': None,
                '申报截止': dead[fam], '备注': note,
                '依据': '%s 年度实施方案共列 %d 个支持方向，没有与本条对应的方向'
                        % (YEAR, len(dirs[fam])),
                '来源本地文件': 'policy-raw/rules/%s.txt' % FAM[fam]['plan'],
            }
            notlisted += 1
            print('ok    %-13s notlisted' % sid)
            continue

        if code not in dirs[fam]:
            print('FAIL  %-13s 方向编号 %s 在实施方案里不存在' % (sid, code))
            bad += 1
            continue
        name, content = dirs[fam][code]
        miss = want - nums(content)
        unexplained = sorted(miss - set(tol))
        if unexplained:
            print('FAIL  %-13s %s 支持内容里缺这些数字且没写原因：%s'
                  % (sid, code, unexplained))
            bad += 1
            continue
        s['年度细则'] = {
            '年度': YEAR, 'st': 'listed', '方向编号': code, '方向': name,
            '申报截止': dead[fam], '备注': note,
            '依据': content.strip(),
            '来源本地文件': 'policy-raw/rules/%s.txt' % FAM[fam]['plan'],
        }
        listed += 1
        tag = ('（容差 %s）' % '；'.join(tol.values())) if miss else ''
        print('ok    %-13s listed  %s %s%s' % (sid, code, name, tag))

    print()
    if bad:
        sys.exit('核验失败 %d 条，一个字都不写' % bad)

    # 年度方案里有、但真理文件没收的方向，显式打出来，别让它悄悄消失
    used = {}
    for sid, (code, _, _) in MAP.items():
        if code:
            used.setdefault(sid.rsplit('-', 1)[0], set()).add(code)
    print('=== 年度方案里有、真理文件没收的方向 ===')
    n_un = 0
    for f in FAM:
        for c, (nm, _) in dirs[f].items():
            if c not in used.get(f, set()):
                print('  %-9s %-9s %s' % (f, c, nm))
                n_un += 1
    print('共 %d 个。它们是真理文件的覆盖缺口，不是本脚本的失败。' % n_un)

    data['年度细则口径'] = (
        '措施是纲领，年度实施方案才决定当年实际开哪几个方向。listed 表示 %s 年度实施方案'
        '列了这一条，notlisted 表示没列、当年报不了。映射手写但逐条过金额数字核验，'
        '核验脚本 shenicest-tool-补贴年度细则标注.py，不过就不落盘。'
        '没有这个字段的条目不走年度制，按 申报窗口 那一套看。' % YEAR)
    with io.open(TRUTH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print()
    print('已写回 %s：listed %d 条，notlisted %d 条'
          % (os.path.basename(TRUTH), listed, notlisted))


if __name__ == '__main__':
    main()

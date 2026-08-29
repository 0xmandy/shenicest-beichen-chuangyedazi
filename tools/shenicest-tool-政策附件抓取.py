# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。

第二遍抓取：把 manifest.json 里那些「印发通知」的附件抓下来。
市政府很多通知正文只是一封印发函，真正写补贴多少钱、什么条件能申请的，
在附件的《办事指南》《实施办法》《认定标准》里。

只收规则类附件（办事指南/办法/措施/细则/标准/条件/方案/指引），
丢掉申报表、承诺书、联系方式、一图读懂这类不含规则的。
html 直接抽正文，pdf 走 pdftotext，doc/docx 走 macOS textutil。

输出：data/policy-raw/att/<父id>-<序号>.txt 与 att/manifest-att.json
"""
import json
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'data', 'policy-raw')
ATT = os.path.join(RAW, 'att')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

KEEP = re.compile(r'办事指南|办法|措施|细则|标准|方案|条件|计划|指引|指南|规定|要求|规划|政策')
DROP = re.compile(r'申报表|承诺书|联系方式|一图读懂|一图懂|图解|读懂|模板|汇总表|名录|'
                  r'申请表|备案表|确认书|调查表|申报书|清单表|咨询电话|问题解答|招生计划表|样表')
AMOUNT_PAT = re.compile(r'[^。；;\n]{0,40}?\d+(?:\.\d+)?\s*(?:万元|亿元)[^。；;\n]{0,40}')

os.makedirs(ATT, exist_ok=True)

# 复用第一遍脚本的正文抽取。取 main() 之前那一段执行，避免把抓取动作也带进来。
_src = open(os.path.join(HERE, 'shenicest-tool-政策原文抓取.py'), encoding='utf-8').read()
_ns = {'__file__': os.path.join(HERE, 'shenicest-tool-政策原文抓取.py')}
exec(compile(_src.split('def main()')[0], 'fetch1', 'exec'), _ns)
strip_tags, extract_body = _ns['strip_tags'], _ns['extract_body']


def to_text(path, url):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.html', '.htm'):
        raw = open(path, encoding='utf-8', errors='ignore').read()
        return extract_body(raw, url)
    if ext == '.pdf':
        r = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', path, '-'],
                           capture_output=True, text=True)
        return r.stdout.strip()
    if ext in ('.doc', '.docx'):
        r = subprocess.run(['textutil', '-convert', 'txt', '-stdout', path],
                           capture_output=True, text=True)
        out = r.stdout.strip()
        if out:
            return out
        # textutil 对某些 doc 会空手而回，退一步当二进制里捞中文
        raw = open(path, 'rb').read().decode('utf-8', 'ignore')
        return re.sub(r'[^一-龥　-〿0-9a-zA-Z%（）()、，。：；．\-\n]', '', raw)
    return ''


def main():
    man = json.load(open(os.path.join(RAW, 'manifest.json'), encoding='utf-8'))
    out = []
    for x in man:
        n = 0
        for a in x['attachments']:
            t = a['text']
            if DROP.search(t) or not KEEP.search(t):
                continue
            n += 1
            href = a['href'].replace('/./', '/')
            ext = os.path.splitext(href.split('?')[0])[1].lower() or '.html'
            if ext not in ('.html', '.htm', '.pdf', '.doc', '.docx'):
                continue
            base = '%s-a%d' % (x['id'], n)
            dst = os.path.join(ATT, base + ext)
            if not (os.path.exists(dst) and os.path.getsize(dst) > 1500):
                r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '-A', UA,
                                    href, '-o', dst, '-w', '%{http_code}'],
                                   capture_output=True, text=True)
                code = r.stdout.strip()
                time.sleep(0.8)
            else:
                code = 'cached'
            txt = to_text(dst, href) if os.path.exists(dst) else ''
            txt = re.sub(r'\n\s*\n+', '\n', txt).strip()
            if len(txt) > 120:
                with open(os.path.join(ATT, base + '.txt'), 'w', encoding='utf-8') as f:
                    f.write('%s\n附于：%s %s\n%s\n%s\n' % (t, x['id'], x['title'], href, '-' * 40))
                    f.write(txt)
            amounts = [s.strip() for s in AMOUNT_PAT.findall(txt)][:12]
            out.append({'id': base, 'parent': x['id'], 'parent_title': x['title'],
                        'text': t, 'href': href, 'http': code,
                        'len': len(txt), 'amounts': amounts})
            print(base, code, len(txt), ('money' if amounts else '-'), t[:34])

    with open(os.path.join(ATT, 'manifest-att.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok = [o for o in out if o['len'] > 120]
    print('\n附件', len(out), '条；抽出正文', len(ok), '条；带具体金额', sum(1 for o in ok if o['amounts']), '条')
    for o in out:
        if o['len'] <= 120:
            print('  抽不出正文：', o['id'], o['http'], o['text'][:40], o['href'][:90])


if __name__ == '__main__':
    main()

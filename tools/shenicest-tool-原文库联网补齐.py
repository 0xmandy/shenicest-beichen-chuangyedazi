# -*- coding: utf-8 -*-
"""属于 shenicest 黑客松北辰命题原型「创业搭子」。

命题方给的《政策智能体数据库.xlsx》第一张表只有 86 个文件名，没有正文
（原文在命题方自己的智能体里）。这个脚本按人工核对过的官方 URL 把这批
文件的正文从政府网站补回本地，好让「补贴多少钱、什么条件能申请」有原文可引。

URL 来自 seed-urls.json，一条政策可以给多个候选地址，按顺序试，
取第一个能抽出足量正文的。抽不到的显式留在缺口清单里，不猜、不编。

朝阳区政府站是 gb2312，北京市政府站是 utf-8，这里按内容探测解码。

输出：
  data/policy-raw/docs/<key>.html / .txt
  data/policy-raw/docs/manifest-docs.json
"""
import json
import os
import re
import html as htmllib
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'data', 'policy-raw')
DOCS = os.path.join(RAW, 'docs')
SEED = os.path.join(HERE, '..', 'data', 'policy-subsidy', 'shenicest-政策原文-seed-urls.json')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
AMOUNT_PAT = re.compile(r'[^。；;\n]{0,40}?\d+(?:\.\d+)?\s*(?:万元|亿元)[^。；;\n]{0,40}')

os.makedirs(DOCS, exist_ok=True)


def decode(raw):
    """政府站编码不统一，用能解出最多汉字的那个。"""
    best, best_n = '', -1
    for enc in ('utf-8', 'gb18030', 'gbk'):
        try:
            t = raw.decode(enc)
        except Exception:
            continue
        n = len(re.findall(r'[一-龥]', t))
        if n > best_n:
            best, best_n = t, n
    return best


def to_text(t):
    t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<(?:br|/p|/div|/tr|/li|/h\d)[^>]*>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    t = htmllib.unescape(t).replace('　', ' ').replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()


def body_of(t):
    """先按常见正文容器切，切不出来就整页转文本。"""
    for start, end in [('div_print', '相关附件'), ('id="mainText"', '分享：'),
                       ('TRS_Editor', '分享：'), ('class="view TRS_UEDITOR', None),
                       ('class="content"', None), ('class="article', None)]:
        i = t.find(start)
        if i < 0:
            continue
        j = t.find(end, i) if end else -1
        txt = to_text(t[i: j if j > i else i + 400000])
        if len(txt) > 500:
            return txt
    return to_text(t)


def fetch_pdf_text(path):
    r = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', path, '-'],
                       capture_output=True, text=True)
    return r.stdout.strip()


def main():
    seeds = json.load(open(SEED, encoding='utf-8'))
    out = []
    for s in seeds:
        key, title, urls = s['key'], s['title'], s['urls']
        picked, txt = None, ''
        for url in urls:
            low = url.lower().split('?')[0]
            ext = next((e for e in ('.pdf', '.docx', '.doc') if low.endswith(e)), '.html')
            dst = os.path.join(DOCS, key + ext)
            if not (os.path.exists(dst) and os.path.getsize(dst) > 1200):
                r = subprocess.run(['curl', '-sS', '-L', '-m', '45', '-A', UA,
                                    url, '-o', dst, '-w', '%{http_code}'],
                                   capture_output=True, text=True)
                time.sleep(0.8)
                if r.stdout.strip() != '200':
                    continue
            if not os.path.exists(dst):
                continue
            if ext == '.pdf':
                cand = fetch_pdf_text(dst)
            elif ext in ('.doc', '.docx'):
                # 政府站的附件常是 doc，macOS 自带 textutil 能转，别拿 HTML 解析器去啃二进制
                rr = subprocess.run(['textutil', '-convert', 'txt', '-stdout', dst],
                                    capture_output=True, text=True)
                cand = rr.stdout.strip()
            else:
                cand = body_of(decode(open(dst, 'rb').read()))
            cand = re.sub(r'\n\s*\n+', '\n', cand).strip()
            # 一图读懂是图片页，抓下来只有导航文字，长度骗人，直接判负
            if '一图读懂' in cand[:200] or '图解' in cand[:120]:
                cand = ''
            if len(cand) > len(txt):
                txt, picked = cand, url
        if len(txt) > 400:
            with open(os.path.join(DOCS, key + '.txt'), 'w', encoding='utf-8') as f:
                f.write('%s\n%s\n%s\n%s\n' % (title, picked, '来源：原文库标题联网补齐', '-' * 40))
                f.write(txt)
        amounts = [a.strip() for a in AMOUNT_PAT.findall(txt)][:12]
        out.append({'key': key, 'title': title, 'url': picked, 'len': len(txt),
                    'amounts': amounts, 'tried': urls})
        print('%-28s %6d %s %s' % (key, len(txt), 'money' if amounts else '-', title[:40]))

    with open(os.path.join(DOCS, 'manifest-docs.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok = [o for o in out if o['len'] > 400]
    print('\n补齐', len(ok), '/', len(out), '份；带具体金额', sum(1 for o in ok if o['amounts']), '份')
    print('没补到的（进待核验缺口）：')
    for o in out:
        if o['len'] <= 400:
            print('  ', o['key'], o['title'][:46])


if __name__ == '__main__':
    main()

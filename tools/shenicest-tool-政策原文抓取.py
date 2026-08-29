# -*- coding: utf-8 -*-
"""由 Claude 生成，属于 shenicest 黑客松北辰命题原型「创业搭子」。

干什么：把《政策智能体数据库.xlsx》第二张表那 89 条政策 URL 逐条抓下来，
存原始 html，抽正文纯文本，识别正文里是不是带钱（万元/补贴/资助/贴息/奖励），
再把「附件」链接找出来（很多市政府通知的正文只是印发函，真规则在附件里）。

不做任何理解与归纳，只落原料。理解那一步在另一个脚本里做，
这样每一条结论都能回链到本地存的原文。

输出：
  data/policy-raw/<id>.html   原始页面
  data/policy-raw/<id>.txt    抽出来的正文纯文本
  data/policy-raw/manifest.json  逐条的元数据与体检结果
"""
import json
import os
import re
import html as htmllib
import time
import subprocess

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('POLICY_XLSX') or os.path.expanduser('~/Downloads/政策智能体数据库.xlsx')
OUT_DIR = os.path.join(HERE, '..', 'data', 'policy-raw')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

MONEY_PAT = re.compile(r'(\d+(?:\.\d+)?\s*(?:万元|亿元|元)|最高不超过|不超过\d|补贴|资助|贴息|奖励|后补助|支持资金|给予.{0,6}支持)')
AMOUNT_PAT = re.compile(r'[^。；;\n]{0,40}?\d+(?:\.\d+)?\s*(?:万元|亿元)[^。；;\n]{0,40}')

os.makedirs(OUT_DIR, exist_ok=True)


def fetch(url, dest):
    """curl 抓页面。带浏览器 UA，政府站对裸 curl 会 403。"""
    if os.path.exists(dest) and os.path.getsize(dest) > 2000:
        return 'cached'
    r = subprocess.run(
        ['curl', '-sS', '-L', '-m', '40', '-A', UA,
         '-H', 'Accept-Language: zh-CN,zh;q=0.9', url, '-o', dest,
         '-w', '%{http_code}'],
        capture_output=True, text=True)
    return r.stdout.strip() or 'ERR'


def strip_tags(seg):
    seg = re.sub(r'<script.*?</script>', ' ', seg, flags=re.S | re.I)
    seg = re.sub(r'<style.*?</style>', ' ', seg, flags=re.S | re.I)
    seg = re.sub(r'<!--.*?-->', ' ', seg, flags=re.S)
    seg = re.sub(r'<(?:br|/p|/div|/tr|/li|/h\d)[^>]*>', '\n', seg, flags=re.I)
    seg = re.sub(r'<[^>]+>', '', seg)
    seg = htmllib.unescape(seg)
    seg = seg.replace('　', ' ').replace('\xa0', ' ')
    seg = re.sub(r'[ \t]+', ' ', seg)
    seg = re.sub(r'\n\s*\n+', '\n', seg)
    return seg.strip()


def extract_body(raw, url):
    """按站点取正文容器。取不到就整页兜底，宁可多噪音也不丢内容。"""
    anchors = []
    if 'ncsti.gov.cn' in url:
        anchors = [('div_print', '相关附件'), ('div_print', None)]
    elif 'beijing.gov.cn' in url:
        anchors = [('mainText', '分享：'), ('TRS_Editor', '分享：'), ('mainTextBox', None)]
    for start_key, end_key in anchors:
        i = raw.find(start_key)
        if i < 0:
            continue
        j = raw.find(end_key, i) if end_key else -1
        seg = raw[i: j if j > i else i + 200000]
        txt = strip_tags(seg)
        if len(txt) > 200:
            return txt
    return strip_tags(raw)


def find_attachments(raw, url):
    """正文里的附件链接。市政府的印发通知常把真规则放附件里。"""
    out = []
    for m in re.finditer(r'href="([^"]+\.(?:html?|pdf|docx?|xlsx?))"[^>]*>([^<]{0,80})', raw, re.I):
        href, text = m.group(1), htmllib.unescape(m.group(2)).strip()
        if not text or href.startswith('#'):
            continue
        if not re.search(r'附件|规划|办法|方案|措施|细则|规定|计划|指引|指南|目录', text):
            continue
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = re.sub(r'^(https?://[^/]+).*', r'\1', url) + href
        elif not href.startswith('http'):
            href = url.rsplit('/', 1)[0] + '/' + href
        if href == url:
            continue
        out.append({'text': text, 'href': href})
    seen, uniq = set(), []
    for a in out:
        if a['href'] in seen:
            continue
        seen.add(a['href'])
        uniq.append(a)
    return uniq[:6]


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['只有url接入到智能体']
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[1] and r[3]]

    manifest = []
    for n, r in enumerate(rows, 1):
        pid = 'R%03d' % n
        title, date, url = str(r[1]).strip(), str(r[2] or '')[:10], str(r[3]).strip()
        dest = os.path.join(OUT_DIR, pid + '.html')
        code = fetch(url, dest)
        if code not in ('200', 'cached'):
            manifest.append({'id': pid, 'title': title, 'date': date, 'url': url,
                             'http': code, 'body_len': 0, 'has_money': False,
                             'amounts': [], 'attachments': []})
            print(pid, code, title[:40])
            time.sleep(1.0)
            continue

        raw = open(dest, encoding='utf-8', errors='ignore').read()
        body = extract_body(raw, url)
        with open(os.path.join(OUT_DIR, pid + '.txt'), 'w', encoding='utf-8') as f:
            f.write(title + '\n' + url + '\n' + '-' * 40 + '\n' + body)
        amounts = [a.strip() for a in AMOUNT_PAT.findall(body)][:12]
        manifest.append({
            'id': pid, 'title': title, 'date': date, 'url': url, 'http': code,
            'body_len': len(body),
            'has_money': bool(MONEY_PAT.search(body)),
            'amounts': amounts,
            'attachments': find_attachments(raw, url),
        })
        print(pid, code, len(body), 'money' if amounts else '-', title[:40])
        if code != 'cached':
            time.sleep(1.0)

    with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    ok = [m for m in manifest if m['body_len'] > 300]
    money = [m for m in ok if m['amounts']]
    thin = [m for m in manifest if m['body_len'] <= 300]
    print('\n抓到', len(manifest), '条；正文可用', len(ok), '条；正文带具体金额', len(money), '条；正文过薄', len(thin), '条')
    print('过薄的（多半正文在附件里）：')
    for m in thin:
        print(' ', m['id'], m['http'], m['body_len'], m['title'][:50], '附件%d' % len(m['attachments']))


if __name__ == '__main__':
    main()

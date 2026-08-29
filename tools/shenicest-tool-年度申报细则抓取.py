# -*- coding: utf-8 -*-
"""由 Claude 生成，属于 shenicest 黑客松北辰命题原型「创业搭子」。

第四遍抓取：把「年度实施细则 / 项目征集通知」抓下来。

为什么要有这一遍：前三遍抓到的是《XX 若干措施》这类纲领文件，它只写补多少钱、
什么条件，不写去哪办、交什么、找谁。补贴条款真理文件里 18 条的办理信息是空的，
根子就在这。朝阳区的措施自己写明了：

    第十六条 朝阳园管委会区科学技术和信息化局负责每年发布政策实施细则，
    制定年度项目征集方案、明确申报流程、受理项目申报、组织项目评审。

所以「申报入口 / 报送地址 / 咨询电话 / 截止日 / 材料清单」住在每年另发的征集通知
和它的附件里，不在措施原文里。这一遍就是去把那批通知和附件捞回来。

两个实测踩到的坑，写在这防止再踩：

1. www.bjchy.gov.cn 声明 charset=gb2312，按 utf-8 读整页全是乱码，且不报错。
   必须按声明编码解码，本脚本统一用 gb18030（gb2312 的超集，能兜住生僻字）。
2. 办理地点不在通知正文里。通知只写一句「详见附件1实施方案」，真正的
   「纸质材料受理部门及联系方式、报送地址」在那个 .xlsx 附件里。
   所以附件必须抓，而且 xlsx 要解析。

输出：
  data/policy-raw/rules/<id>.html          原始页面
  data/policy-raw/rules/<id>.txt           正文纯文本
  data/policy-raw/rules/<id>-a<n>.<ext>    附件原件
  data/policy-raw/rules/<id>-a<n>.txt      附件纯文本
  data/policy-raw/rules/manifest-rules.json  逐条元数据与体检结果

只落原料，不做理解与归纳。理解那一步在底稿里做，每条结论都能回链本地原文。
"""
import html as htmllib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'data', 'policy-raw')
OUT = os.path.join(RAW, 'rules')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

# 要翻的列表栏目。找对栏目花了三次试错，过程记在这，别再走一遍：
#
# 1 /slh/gsgg/          长者版公示公告。30 页封顶，只回溯到 2026-07-06。
#                       年度征集通知发在 3、4 月，全被截在窗口外，命中 0 条。
# 2 /dynamic/notice/    正常版公示公告。50 页、回溯到 2026-03-23、带发布部门，
#                       但 5 个月里朝阳园管委会只发了 19 条，全是名单公示与认定，
#                       一条产业资金征集通知都没有。栏目不对。
# 3 /affair/file/otherfile/  政务公开>>政策文件>>部门文件。27 页、回溯到 2002 年，
#                       年度征集通知真正住在这。这才是对的入口。
#
# 两个栏目都翻：otherfile 拿征集通知，notice 兜住临时性的场景征集与认定批次。
LISTS = [
    {'name': 'CHY-DOC', 'base': 'http://www.bjchy.gov.cn/affair/file/otherfile/', 'pages': 27},
    {'name': 'CHY-GG', 'base': 'http://www.bjchy.gov.cn/dynamic/notice/', 'pages': 50},
]

# 只要这些部门发的。产业资金归朝阳园管委会（区科信局），别的部门的公示不看。
DEPT_KEEP = re.compile(r'朝阳园|科学技术和信息化局|科信局|发展改革委|经济和信息化')

# 标题命中才抓正文。宁可多抓，后面人工对。
TITLE_KEEP = re.compile(r'征集|申报|实施方案|实施细则|兑现|拨付|资金|支持项目|办事指南')
# 明显与产业资金无关的先丢，省请求。
TITLE_DROP = re.compile(r'社会救助|财物招领|执业登记|代理记账|遴选结果|中标|成交|招标|'
                        r'拟聘|招聘|人事|任免|抽检|监督检查|行政处罚|复核结果|录取')

# 这一遍关心的主题：18 条空白项落在人工智能、数据要素、OPC、专精特新上。
# 互联网3.0 与数字医疗虽然本地正文有线索，但线索里没有地址，顺手一起抓。
TOPIC = re.compile(r'人工智能|大模型|算力|数据要素|数据|OPC|互联网3\.0|互联网 ?3|'
                   r'数字医疗|专精特新|科技创新券|高精尖')

# 单独点名抓的页面：市级与区级的 OPC，走各自发布口，不在朝阳公示公告列表里。
SEEDS = [
    {'id': 'RULE-OPC-CHY',
     'title': '朝阳区关于支持人工智能OPC创新发展的若干措施（印发通知）',
     'url': 'http://www.bjchy.gov.cn/affair/file/otherfile/4028805a9dfdb457019e25a981de22c6.html'},
]

ATT_EXT = ('.xlsx', '.xls', '.docx', '.doc', '.pdf', '.zip', '.html', '.htm')

os.makedirs(OUT, exist_ok=True)


def curl(url, dest, timeout=60):
    """抓页面。带浏览器 UA，政府站对裸 curl 会 403。返回 http 状态码字符串。"""
    if os.path.exists(dest) and os.path.getsize(dest) > 1200:
        return 'cached'
    r = subprocess.run(
        ['curl', '-sS', '-L', '-m', str(timeout), '-A', UA,
         '-H', 'Accept-Language: zh-CN,zh;q=0.9', url, '-o', dest,
         '-w', '%{http_code}'],
        capture_output=True, text=True)
    time.sleep(0.6)
    return (r.stdout or '').strip() or 'ERR'


def read_page(path):
    """按页面声明的 charset 解码。bjchy 是 gb2312，用 utf-8 读会静默变乱码。"""
    raw = open(path, 'rb').read()
    m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:4000])
    enc = (m.group(1).decode('ascii', 'ignore').lower() if m else 'utf-8')
    if enc in ('gb2312', 'gbk', 'gb18030'):
        enc = 'gb18030'
    try:
        return raw.decode(enc, errors='replace')
    except LookupError:
        return raw.decode('utf-8', errors='replace')


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


def page_key(url):
    """从 URL 里的页面 hash 取一个稳定短 id。同一条通知永远落同一个文件名。"""
    m = re.search(r'([0-9a-f]{24,})\.html', url)
    return (m.group(1)[-10:] if m else re.sub(r'\W+', '', url)[-10:])


def list_page_url(base, i):
    return base + ('index.html' if i == 0 else 'index_%d.html' % i)


def parse_list(txt, base):
    """从列表页抽 (日期, 部门, 标题, 绝对URL)。

    /dynamic/notice/ 的条目长这样：

        <li><span>[2026-08-28]</span>
            <em class="rootin" onclick="...">[区卫生健康委]</em>
            <a href='<一堆制表符和换行><hash>.html<一堆制表符>' class="news">标题...</a></li>

    两个坑：
    - href 里塞满了 \\r\\n\\t，必须把所有空白都去掉才拼得出可用地址
    - 列表里的标题是截断的（尾部带省略号），所以筛选放宽，正文抓回来再看全名

    /affair/file/otherfile/ 是第三套：href 写的是绝对地址，且没有部门那个 <em>。
    /slh/gsgg/ 长者版是第四套（div.date + div.tit + 夹一个空 <i>）。
    四套一并兼容，换栏目时不用改代码。
    """
    out = []
    for li in re.split(r'<li[^>]*>', txt)[1:]:
        d = re.search(r'<span>\s*\[?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', li) \
            or re.search(r'class="date"[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', li)
        dept = re.search(r'class="rootin"[^>]*>\s*\[?([^<\]]{2,30})\]?\s*</em>', li)
        a = re.search(r'href=["\']([\s\S]*?[0-9a-f]{24,}\.html)[\s\S]*?["\']'
                      r'[^>]*>((?:\s*<[^>]*>)*)\s*([^<]{4,200})', li)
        if not a:
            continue
        href = re.sub(r'\s+', '', a.group(1))
        if not href.startswith('http'):
            href = base + href.lstrip('/')
        title = re.sub(r'\s+', ' ', htmllib.unescape(a.group(3))).strip()
        out.append((d.group(1) if d else '',
                    (dept.group(1).strip(' []') if dept else ''),
                    title, href))
    return out


def find_attachments(txt, page_url):
    """抽附件链接。朝阳站的附件统一挂在 /UserFiles/File/ 下。"""
    out, seen = [], set()
    for m in re.finditer(r'href=["\']([^"\']+)["\'][^>]*>\s*([^<]{0,120})', txt):
        href, text = m.group(1).strip(), htmllib.unescape(m.group(2)).strip()
        ext = os.path.splitext(href.split('?')[0])[1].lower()
        if ext not in ATT_EXT:
            continue
        if ext in ('.html', '.htm') and '/UserFiles/' not in href:
            continue
        if href.startswith('//'):
            href = 'http:' + href
        elif href.startswith('/'):
            href = re.sub(r'^(https?://[^/]+).*', r'\1', page_url) + href
        elif not href.startswith('http'):
            href = page_url.rsplit('/', 1)[0] + '/' + href
        if href in seen or href == page_url:
            continue
        seen.add(href)
        out.append({'text': text, 'href': href})
    return out[:8]


def xlsx_to_text(path):
    """实施方案常年是表格，报送地址与受理部门就在某个单元格里。逐表逐行拼。

    两种格式都要认：新的 .xlsx 走 openpyxl，WPS 存的老 .xls 走 xlrd。
    只上 openpyxl 会在 .xls 上静默退化成一句报错文本（149 字），
    体检里看着像“成功”，实则整份实施方案一个字没抽到。
    """
    ext = os.path.splitext(path)[1].lower()
    buf = []
    if ext == '.xls':
        try:
            import xlrd
            wb = xlrd.open_workbook(path)
        except Exception as e:
            return '[xls 打不开：%s]' % e
        for ws in wb.sheets():
            buf.append('### 工作表：%s' % ws.name)
            for i in range(ws.nrows):
                cells = [str(c.value).strip() for c in ws.row(i) if str(c.value).strip()]
                if cells:
                    buf.append(' | '.join(cells))
        return '\n'.join(buf)
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        return '[xlsx 打不开：%s]' % e
    for ws in wb.worksheets:
        buf.append('### 工作表：%s' % ws.title)
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                buf.append(' | '.join(cells))
    return '\n'.join(buf)


def run(cmd):
    """跑外部命令并拿 stdout。

    统一走 bytes 再自己解码：unzip 列中文文件名时吐的是 GBK，
    subprocess 的 text=True 按 utf-8 解会直接抛 UnicodeDecodeError 把整个脚本崩掉。
    """
    r = subprocess.run(cmd, capture_output=True)
    out = r.stdout or b''
    for enc in ('utf-8', 'gb18030'):
        try:
            return out.decode(enc)
        except UnicodeDecodeError:
            continue
    return out.decode('utf-8', 'replace')


def att_to_text(path, url, depth=0):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.xlsx', '.xls'):
        return xlsx_to_text(path)
    if ext == '.pdf':
        return run(['pdftotext', '-layout', '-enc', 'UTF-8', path, '-']).strip()
    if ext in ('.doc', '.docx'):
        out = run(['textutil', '-convert', 'txt', '-stdout', path]).strip()
        if out:
            return out
        raw = open(path, 'rb').read().decode('utf-8', 'ignore')
        return re.sub(r'[^一-龥　-〿0-9a-zA-Z%（）()、，。：；．\-\n]', '', raw)
    if ext in ('.html', '.htm'):
        return strip_tags(read_page(path))
    if ext == '.zip' and depth == 0:
        # 解开再逐个转。实施方案有时是打包进 zip 一起发的，只列文件名会漏掉正文。
        #
        # 不能用命令行 unzip：包里的文件名是 GBK，macOS 自带的 Info-ZIP 不认 -O 参数，
        # 不带 -O 又会在建目录时 "Illegal byte sequence" 直接罢工，且退出码仍是 0。
        # 所以走 Python zipfile，自己按 gb18030 还原文件名，落盘时换成安全名。
        import zipfile
        d = path[:-4] + '_unzip'
        os.makedirs(d, exist_ok=True)
        buf = ['[zip 包解开后内含]']
        try:
            with zipfile.ZipFile(path) as z:
                for i, info in enumerate(z.infolist()[:12]):
                    if info.is_dir():
                        continue
                    try:
                        name = info.filename.encode('cp437').decode('gb18030')
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        name = info.filename
                    inner_ext = os.path.splitext(name)[1].lower() or '.bin'
                    if os.path.basename(name).startswith('~$'):
                        continue          # Office 的临时锁文件，不是内容
                    fp = os.path.join(d, 'f%02d%s' % (i, inner_ext))
                    with open(fp, 'wb') as f:
                        f.write(z.read(info))
                    buf.append('### %s' % name)
                    buf.append(att_to_text(fp, url, depth + 1)[:20000])
        except Exception as e:
            return '[zip 解不开：%s]' % e
        return '\n'.join(buf)
    return ''


def harvest(rid, title, url, report):
    """抓一条通知：正文 + 附件。落盘并记账。"""
    page = os.path.join(OUT, rid + '.html')
    code = curl(url, page)
    rec = {'id': rid, 'title': title, 'url': url, 'http': code,
           'body_chars': 0, 'attachments': [], 'ok': False, 'fail': None}
    if not os.path.exists(page) or os.path.getsize(page) < 1200:
        rec['fail'] = 'http=%s 页面为空或过小' % code
        report.append(rec)
        return rec
    txt = read_page(page)
    body = strip_tags(txt)
    rec['body_chars'] = len(body)
    with open(os.path.join(OUT, rid + '.txt'), 'w', encoding='utf-8') as f:
        f.write('%s\n%s\n%s\n' % (title, url, '-' * 50))
        f.write(body)
    for n, a in enumerate(find_attachments(txt, url), 1):
        ext = os.path.splitext(a['href'].split('?')[0])[1].lower()
        base = '%s-a%d' % (rid, n)
        dst = os.path.join(OUT, base + ext)
        acode = curl(a['href'], dst)
        arec = {'n': n, 'text': a['text'], 'href': a['href'], 'http': acode,
                'chars': 0, 'fail': None}
        if os.path.exists(dst) and os.path.getsize(dst) > 200:
            at = re.sub(r'\n\s*\n+', '\n', att_to_text(dst, a['href'])).strip()
            arec['chars'] = len(at)
            if len(at) > 60:
                with open(os.path.join(OUT, base + '.txt'), 'w', encoding='utf-8') as f:
                    f.write('%s\n附于：%s %s\n%s\n%s\n' % (a['text'], rid, title,
                                                        a['href'], '-' * 50))
                    f.write(at)
            else:
                arec['fail'] = '转文本后不足 60 字，可能是扫描件或转换失败'
        else:
            arec['fail'] = 'http=%s 下载失败' % acode
        rec['attachments'].append(arec)
    rec['ok'] = rec['body_chars'] > 200
    if not rec['ok']:
        rec['fail'] = '正文不足 200 字'
    report.append(rec)
    return rec


def main():
    report = []
    # ---- 1 翻列表页，筛候选 ----
    cands, list_fail, cover = [], [], []
    for col in LISTS:
        dates, n_items, n_fail = [], 0, 0
        for i in range(col['pages']):
            u = list_page_url(col['base'], i)
            p = os.path.join(OUT, '_list_%s_%02d.html' % (col['name'], i))
            code = curl(u, p)
            if not os.path.exists(p) or os.path.getsize(p) < 1200:
                list_fail.append({'col': col['name'], 'page': i, 'url': u, 'http': code})
                n_fail += 1
                continue
            items = parse_list(read_page(p), col['base'])
            if not items:
                list_fail.append({'col': col['name'], 'page': i, 'url': u,
                                  'http': code, 'why': '解析出 0 条'})
                n_fail += 1
            n_items += len(items)
            dates += [d for d, _, _, _ in items if d]
            for date, dept, title, link in items:
                if TITLE_DROP.search(title):
                    continue
                # 两条命中路径，取并集：
                #   A 标题自带主题词（题材对得上，不论哪个部门发的）
                #   B 产业口部门发的申报类通知（标题被截断、主题词掉在省略号后面时兜住）
                hit_a = TITLE_KEEP.search(title) and TOPIC.search(title)
                hit_b = DEPT_KEEP.search(dept) and TITLE_KEEP.search(title)
                if hit_a or hit_b:
                    cands.append((date, dept or col['name'], title, link))
        span = ('%s ~ %s' % (min(dates), max(dates))) if dates else '无日期'
        cover.append({'栏目': col['name'], 'base': col['base'], '页数': col['pages'],
                      '条目数': n_items, '日期区间': span, '失败页数': n_fail})
        print('%s：%d 页 / %d 条 / 覆盖 %s / 失败 %d 页'
              % (col['name'], col['pages'], n_items, span, n_fail))
    # 去重，保序
    seen, uniq = set(), []
    for d, dp, t, l in cands:
        if l in seen:
            continue
        seen.add(l)
        uniq.append((d, dp, t, l))
    print('命中候选 %d 条' % len(uniq))
    for d, dp, t, _ in uniq:
        print('   -', d, '[%s]' % dp, t[:64])

    # ---- 2 抓候选与点名种子 ----
    # id 从 URL 里的页面 hash 派生，不用序号。
    # 用序号踩过一次：候选集顺序会随筛选条件变，而 curl 按目标路径命中缓存，
    # 于是上一轮 RULE-CHY-04 的附件被这一轮完全不同的一条通知当成自己的附件读走了，
    # 而且全程 http=cached、零报错。序号命名 + 缓存 = 静默串档。
    for d, dp, t, l in uniq:
        harvest('RULE-CHY-' + page_key(l), t, l, report)
    for s in SEEDS:
        harvest(s['id'], s['title'], s['url'], report)

    # ---- 3 体检：失败必须显式列出进分母，不许吞掉 ----
    man = {
        '说明': '本文件由 Claude 生成，属于 shenicest 黑客松北辰命题原型「创业搭子」。'
                '年度实施细则与项目征集通知的抓取台账。',
        '抓取日': time.strftime('%Y-%m-%d'),
        '列表覆盖': cover,
        '列表页失败': list_fail,
        '条目': report,
    }
    with open(os.path.join(OUT, 'manifest-rules.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in report if r['ok'])
    att_all = sum(len(r['attachments']) for r in report)
    att_ok = sum(1 for r in report for a in r['attachments'] if not a['fail'])
    print()
    print('正文 %d/%d 成功' % (ok, len(report)))
    print('附件 %d/%d 成功' % (att_ok, att_all))
    if list_fail:
        print('列表页失败 %d 页：%s' % (len(list_fail), [x['page'] for x in list_fail]))
    for r in report:
        if r['fail']:
            print('  正文失败 %s %s：%s' % (r['id'], r['title'][:30], r['fail']))
        for a in r['attachments']:
            if a['fail']:
                print('  附件失败 %s-a%d %s：%s' % (r['id'], a['n'], a['text'][:26], a['fail']))
    # 有失败就非 0 退出，让调用方知道这批数据不完整
    sys.exit(0 if (ok == len(report) and att_ok == att_all and not list_fail) else 1)


if __name__ == '__main__':
    main()

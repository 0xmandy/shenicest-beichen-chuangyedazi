#!/usr/bin/env python3
# 本文件属于 shenicest 黑客松「创业搭子」。
# 把产品方案文档那份 Markdown 按六个交付项拆成六份 docx，图用先渲染好的 PNG。
#
# 前置：先跑 chuangyedazi-tool-出mermaid图png.py 出 figs/fig*.png
# 用法：python3 chuangyedazi-tool-出docx分册.py
# 依赖：pandoc

import io
import os
import re
import shutil
import subprocess
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.environ.get(
    "CYD_MD",
    os.path.join(
        HERE, "..", "docs", "shenicest-北辰-创业搭子-产品方案文档-2026-08-29.md"
    ),
)
FIGS = os.path.join(HERE, "figs")
OUT = os.environ.get("CYD_DOCX_DIR", os.path.join(HERE, "docx"))
REF = os.path.join(HERE, "ref-cn.docx")

VERSION = "v1.1，2026-08-29"
PROTO = "https://chuangyedazi.pages.dev"
API = "https://chuangyedazi-api.safepanda.workers.dev/"

# 六个分册：文件名序号、册名、吃主文档的哪一节、本册要带上的缺口条目序号
PARTS = [
    ("01", "产品定位与目标用户画像", "一、产品定位与目标用户画像", [3, 4]),
    ("02", "核心功能架构图", "二、核心功能架构（五大模块如何串联）", [5]),
    ("03", "核心用户旅程流程图", "三、核心用户旅程", [9]),
    ("04", "创新点说明", "四、创新点：与现有园区服务平台的差异化", [1]),
    ("05", "商业模式与运营策略", "五、商业模式与运营策略", [2, 7, 8]),
    ("06", "数据安全与隐私合规", "六、数据安全与隐私合规", [6]),
]

INDEX_TABLE = """| 分册 | 对应交付要求 |
|---|---|
| 一 | 产品定位与目标用户画像 |
| 二 | 核心功能架构图（五大模块如何串联） |
| 三 | 至少 3 个核心用户旅程的完整流程图 |
| 四 | 创新点说明（与现有园区服务平台的差异化） |
| 五 | 商业模式与运营策略（含 Token / 积分激励设计） |
| 六 | 数据安全与隐私合规考量 |
"""

SOURCE_TABLE = """| 标注 | 含义 |
|---|---|
| 库内 | 命题方给的政策库、金融工具库原字段，或政府网站政策原文，可回链 |
| 派生 | 由库内数据算出来的统计量，算法在仓库脚本里 |
| 方案 | 本文档提出的设计与假设，尚未实现或尚未与命题方核对 |
"""

CN_NUM = {"01": "一", "02": "二", "03": "三", "04": "四", "05": "五", "06": "六"}


def build_reference():
    """出一份中文排版的 pandoc 参考 docx：A4、2.2cm 页边距、正文微软雅黑 10.5pt。"""
    base = os.path.join(HERE, "ref-base.docx")
    if not os.path.exists(base):
        with open(base, "wb") as f:
            subprocess.check_call(
                ["pandoc", "--print-default-data-file", "reference.docx"], stdout=f
            )
    work = os.path.join(HERE, "refwork")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    with zipfile.ZipFile(base) as z:
        z.extractall(work)

    sp = os.path.join(work, "word", "styles.xml")
    s = io.open(sp, encoding="utf-8").read()
    # 正文字体与字号。eastAsia 给微软雅黑，装不上时 Word 会自己回退，不会变方块
    s = s.replace(
        '<w:rFonts w:asciiTheme="minorHAnsi" w:eastAsiaTheme="minorEastAsia" '
        'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi" />\n        <w:sz w:val="24" />\n'
        '        <w:szCs w:val="24" />',
        '<w:rFonts w:ascii="Calibri" w:eastAsia="微软雅黑" w:hAnsi="Calibri" w:cs="Calibri" />\n'
        '        <w:sz w:val="21" />\n        <w:szCs w:val="21" />',
        1,
    )
    # 行距放到 1.5，中文密排看着累
    s = s.replace(
        '<w:pPr>\n        <w:spacing w:after="200" />\n      </w:pPr>',
        '<w:pPr>\n        <w:spacing w:after="140" w:line="330" w:lineRule="auto" />\n      </w:pPr>',
        1,
    )
    io.open(sp, "w", encoding="utf-8").write(s)

    dp = os.path.join(work, "word", "document.xml")
    d = io.open(dp, encoding="utf-8").read()
    # A4 竖版 + 2.2cm 页边距。twips：1cm = 567
    d = d.replace(
        "<w:sectPr>",
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838" />'
        '<w:pgMar w:top="1247" w:right="1247" w:bottom="1247" w:left="1247" '
        'w:header="709" w:footer="709" w:gutter="0" />',
        1,
    )
    io.open(dp, "w", encoding="utf-8").write(d)

    if os.path.exists(REF):
        os.remove(REF)
    with zipfile.ZipFile(REF, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(work):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, work))
    print("参考样式 %s" % os.path.basename(REF))


def split_master():
    """按二级标题切主文档，返回 {标题: 正文}。"""
    md = io.open(MD, encoding="utf-8").read()
    parts = re.split(r"\n## ", md)
    out = {}
    for chunk in parts[1:]:
        title, body = chunk.split("\n", 1)
        out[title.strip()] = body.strip()
    return out, md


def gaps(md):
    """第八节的缺口逐条取出来，按序号返回。"""
    sec = md.split("## 八、待核验缺口", 1)[1]
    items = re.findall(r"^\d+\.\s+(.+)$", sec, re.M)
    return {i + 1: t for i, t in enumerate(items)}


def fig_size(path):
    """按图的长宽比给 pandoc 的尺寸属性：宽的卡宽度，高的卡高度，都保证印出来能读。"""
    from PIL import Image

    w, h = Image.open(path).size
    max_w, max_h = 16.6, 21.0  # cm，A4 减掉页边距
    if w / h >= max_w / max_h:
        return "width=%.1fcm" % max_w
    return "height=%.1fcm" % max_h


def main():
    build_reference()
    os.makedirs(OUT, exist_ok=True)
    sections, md = split_master()
    gap_map = gaps(md)

    fig_no = [0]  # 全局图号，按图在主文档里出现的顺序走

    def sub_fig(m):
        fig_no[0] += 1
        path = os.path.join(FIGS, "fig%d.png" % fig_no[0])
        if not os.path.exists(path):
            raise SystemExit("缺图 %s，先跑 出mermaid图png.py" % path)
        return "![](%s){%s}" % (path, fig_size(path))

    # 先把整篇的 mermaid 块按顺序换成图片，保证图号与渲染顺序一致
    for k in list(sections):
        sections[k] = re.sub(r"```mermaid\n.*?```", sub_fig, sections[k], flags=re.S)

    for num, name, sec_title, gap_ids in PARTS:
        body = sections.get(sec_title)
        if body is None:
            raise SystemExit("主文档里找不到这一节：%s" % sec_title)

        # 标题自带 1.1 这样的编号，目录再套一层有序列表会变成「1. 1.1 …」，用无序列表
        toc = "\n".join(
            "- %s" % t for t in re.findall(r"^### (.+)$", body, re.M)
        ) + "\n- 本册相关的待核验缺口\n"

        # 目录算完再把节内三级标题降一级，让分册自己的一级标题当册名
        body = re.sub(r"^### ", "## ", body, flags=re.M)

        gap_lines = "\n".join(
            "%d. %s" % (i, gap_map[i]) for i in gap_ids if i in gap_map
        )
        doc = """---
title: "创业搭子 · 产品方案文档（%s）%s"
subtitle: "She Nicest Hackathon 2026 · 北辰产业云社区命题"
---

本文件属于 She Nicest Hackathon 2026 北辰产业云社区命题的参赛项目「创业搭子」。这是产品方案文档六份分册中的第%s份。

| 项 | 内容 |
|---|---|
| 版本 | %s |
| 本册对应交付要求 | %s |
| 线上原型 | %s |
| 开放层（MCP / API / Skill） | %s |

**目录**

%s
**六份分册**

%s
**文中数字的来源标注**

%s
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# %s

%s

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# 本册相关的待核验缺口

这一节存在的理由是：本产品的核心主张是不生成没有依据的内容，那么方案文档本身也不该把没做的说成做了的。

%s
""" % (
            CN_NUM[num], name,
            CN_NUM[num],
            VERSION,
            name,
            PROTO,
            API,
            toc,
            INDEX_TABLE,
            SOURCE_TABLE,
            name,
            body,
            gap_lines or "本册没有单独的待核验缺口。",
        )
        src = os.path.join(OUT, "%s.md" % num)
        io.open(src, "w", encoding="utf-8").write(doc)
        dst = os.path.join(OUT, "%s-%s.docx" % (num, name))
        subprocess.check_call(
            [
                "pandoc", src,
                "--reference-doc", REF,
                "-f", "markdown",
                "-o", dst,
            ]
        )
        os.remove(src)
        print("出 %s（%d KB）" % (os.path.basename(dst), os.path.getsize(dst) // 1024))

    print("共用图 %d 张" % fig_no[0])


if __name__ == "__main__":
    main()

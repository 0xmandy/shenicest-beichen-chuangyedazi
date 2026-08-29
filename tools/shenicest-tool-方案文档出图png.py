#!/usr/bin/env python3
# 本文件属于 shenicest 黑客松「创业搭子」。
# 把方案文档里的 mermaid 图逐张渲染成 PNG，供 docx 嵌入。
# 做法：无头 Chrome 渲染 mermaid 到定宽白底页面，截图后用 Pillow 按白色裁掉留白。
# 两倍缩放截图保证在 Word 里放大不糊。

import io
import os
import re
import subprocess
import sys
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.environ.get(
    "CYD_MD",
    os.path.join(
        HERE, "..", "docs", "shenicest-北辰-创业搭子-产品方案文档-2026-08-29.md"
    ),
)
OUT = os.path.join(HERE, "figs")
CHROME = os.environ.get(
    "CYD_CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
# 渲染画布。宽度给足，图窄了 mermaid 会强行折行把标签压扁；高度给足，截不全比裁多了难修
CANVAS_W, CANVAS_H, SCALE = 1500, 3000, 2

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<script>%s</script>
<style>
 html,body{margin:0;padding:0;background:#fff}
 #box{padding:20px;width:%dpx;background:#fff;
  font:15px/1.6 "PingFang SC","Hiragino Sans GB",-apple-system,sans-serif}
 .mermaid{background:#fff}
 .mermaid svg{max-width:100%%;height:auto}
</style></head><body><div id="box"><div class="mermaid" id="m"></div></div>
<script>
document.getElementById('m').textContent = %s;
mermaid.initialize({startOnLoad:false, theme:'neutral',
  flowchart:{useMaxWidth:false, htmlLabels:true, nodeSpacing:38, rankSpacing:48},
  themeVariables:{fontFamily:'PingFang SC, Hiragino Sans GB, sans-serif', fontSize:'15px'}});
mermaid.run();
</script></body></html>"""


def render(idx, code):
    src = os.path.join(OUT, "fig%d.html" % idx)
    shot = os.path.join(OUT, "fig%d-raw.png" % idx)
    final = os.path.join(OUT, "fig%d.png" % idx)
    mermaid_js = io.open(os.path.join(HERE, "mermaid.min.js"), encoding="utf-8").read()
    # 图代码走 JSON 塞进 textContent，别拼进 HTML：里面有引号和 <br/>
    import json

    io.open(src, "w", encoding="utf-8").write(
        PAGE % (mermaid_js, CANVAS_W - 40, json.dumps(code, ensure_ascii=False))
    )
    profile = "/tmp/cydfig-%d" % idx
    subprocess.Popen(
        [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--virtual-time-budget=12000",
            "--force-device-scale-factor=%d" % SCALE,
            "--window-size=%d,%d" % (CANVAS_W, CANVAS_H),
            "--user-data-dir=" + profile,
            "--screenshot=" + shot,
            "file://" + src,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return shot, final, profile


def autocrop(shot, final):
    im = Image.open(shot).convert("RGB")
    # 白底裁边：找出所有非白像素的包围盒，四周各留 16px
    from PIL import ImageChops

    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    if not box:
        raise SystemExit("图是空白的：%s" % shot)
    pad = 16
    l, t, r, b = box
    box = (max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad))
    im.crop(box).save(final, "PNG")
    return im.crop(box).size


def main():
    os.makedirs(OUT, exist_ok=True)
    md = io.open(MD, encoding="utf-8").read()
    blocks = re.findall(r"```mermaid\n(.*?)```", md, re.S)
    print("找到 %d 张图" % len(blocks))
    jobs = [render(i, b) for i, b in enumerate(blocks, 1)]
    # 无头 Chrome 截完常常不退，轮询产物别 wait（README 记过这个坑）
    for _ in range(60):
        if all(os.path.exists(s) and os.path.getsize(s) > 0 for s, _, _ in jobs):
            break
        time.sleep(2)
    time.sleep(2)
    subprocess.call(["pkill", "-f", "user-data-dir=/tmp/cydfig-"])
    for i, (shot, final, _) in enumerate(jobs, 1):
        if not os.path.exists(shot) or os.path.getsize(shot) == 0:
            print("fig%d 截图没出来" % i, file=sys.stderr)
            continue
        w, h = autocrop(shot, final)
        os.remove(shot)
        print("fig%d.png  %dx%d" % (i, w, h))


if __name__ == "__main__":
    main()

#!/bin/zsh
# 把原型里的 <script> 段抽出来做 node --check。
# 属于 shenicest 黑客松北辰命题「创业搭子」。
#
# 用法：zsh tools/shenicest-tool-语法自查.sh
# 改完 html 第一件事就是跑它。整行删代码留下的悬空 + 号这类错，只有它逮得到。
set -e
ROOT="${0:A:h:h}"
HTML="${CYD_HTML:-$ROOT/shenicest-北辰-创业搭子-原型-2026-08-27.html}"
OUT="$ROOT/qa-out/check.js"

[[ -f "$HTML" ]] || { echo "找不到原型 html：$HTML"; exit 1; }
mkdir -p "$ROOT/qa-out"

python3 - "$HTML" "$OUT" <<'PY'
import io, re, sys
s = io.open(sys.argv[1], encoding='utf-8').read()
blocks = re.findall(r'<script[^>]*>(.*?)</script>', s, re.S)
io.open(sys.argv[2], 'w', encoding='utf-8').write("\n".join(blocks))
print("抽出 %d 段 script，共 %d 字符" % (len(blocks), sum(len(b) for b in blocks)))
PY

node --check "$OUT" && echo "JS 语法 OK"

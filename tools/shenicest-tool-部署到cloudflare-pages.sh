#!/bin/zsh
# 把原型部署到 Cloudflare Pages。属于 shenicest 黑客松北辰命题「创业搭子」。
#
# 用法：zsh tools/shenicest-tool-部署到cloudflare-pages.sh
# 线上地址 https://chuangyedazi.pages.dev
#
# 部署目录是 repo 下的 dist/（已进 .gitignore）。只往里放 index.html 与 _headers，
# 别直接 deploy repo 根目录，否则 .py 脚本和文档会跟着上公网。
#
# wrangler 的 OAuth 令牌会过期。过期了在交互终端跑：npx --yes wrangler@latest login
set -e
ROOT="${0:A:h:h}"
HTML="${CYD_HTML:-$ROOT/shenicest-北辰-创业搭子-原型-2026-08-27.html}"
DIST="$ROOT/dist"
PROJECT="${CYD_PAGES_PROJECT:-chuangyedazi}"

[[ -f "$HTML" ]] || { echo "找不到原型 html：$HTML"; exit 1; }

# 上线前先过一遍语法，省得把坏的 JS 推上去
zsh "$ROOT/tools/shenicest-tool-语法自查.sh"

mkdir -p "$DIST"
cp "$HTML" "$DIST/index.html"
printf '/*\n  X-Frame-Options: SAMEORIGIN\n  Referrer-Policy: no-referrer\n' > "$DIST/_headers"

cd "$DIST"
npx --yes wrangler@latest pages deploy . --project-name "$PROJECT" --branch main --commit-dirty=true

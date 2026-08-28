# -*- coding: utf-8 -*-
"""第三趟：把剩下的 emoji 全部清掉。UI 图标换内联 SVG，文案里的换文字标签。
收尾时断言全文不再有象形 emoji，有残留就报错退出。"""
import io, sys, re

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-Claude-2026-08-27.html"
src = io.open(PATH, encoding="utf-8").read()

def repn(old, new, times, label):
    global src
    n = src.count(old)
    if n != times:
        sys.exit("锚点[%s]命中 %d 次，应为 %d 次，退出" % (label, n, times))
    src = src.replace(old, new)
    print("  ok  %s（%d）" % (label, times))

def s(name, size=18):
    return '<svg class="ic ic-%d"><use href="#i-%s"></use></svg>' % (size, name)

# --- 冷启动 ---
repn('<div class="ob-welcome-icon">🚀</div>', '<div class="ob-welcome-icon">' + s("spark", 40) + '</div>', 1, "冷启动主图")
repn('<span class="ob-tag">📋 175 条政策库</span>', '<span class="ob-tag">' + s("doc", 16) + ' 175 条政策库</span>', 1, "标签1")
repn('<span class="ob-tag">🏦 67 个金融产品</span>', '<span class="ob-tag">' + s("bank", 16) + ' 67 个金融产品</span>', 1, "标签2")
repn('<span class="ob-tag">💬 答不上就说答不上</span>', '<span class="ob-tag">' + s("chat", 16) + ' 答不上就说答不上</span>', 1, "标签3")
for emo, icon in [("🏢", "biz"), ("📝", "edit"), ("🎓", "grad"), ("📜", "file"),
                  ("🌊", "globe"), ("🗺️", "flag"), ("🏠", "home")]:
    repn('<span class="ob-option-icon">%s</span>' % emo,
         '<span class="ob-option-icon">%s</span>' % s(icon, 20), 1, "冷启动选项 " + icon)
repn('<span class="ob-check">✓</span>', '<span class="ob-check">' + s("check", 16) + '</span>', 7, "冷启动勾选")
repn('>完成 ✓</button>', '>完成</button>', 1, "完成按钮")

# --- 小事广场头部与活动卡 ---
repn('<div class="plaza-helper-title">💡 小事广场</div>',
     '<div class="plaza-helper-title">' + s("bolt", 16) + ' 小事广场</div>', 1, "广场标题")
repn('                            📋 我的小事\n',
     '                            ' + s("book", 16) + ' 我的小事\n', 1, "我的小事按钮")
repn('<div class="activity-icon">🎤</div>', '<div class="activity-icon">' + s("mic", 22) + '</div>', 1, "活动图标")
repn('margin-right:4px;">🌱 生态</span>', 'margin-right:4px;">生态</span>', 1, "生态标签")
repn('<span>📅 9月3日 周四 14:00</span>', '<span>' + s("calendar", 16) + ' 9月3日 周四 14:00</span>', 1, "活动时间")
repn('<span>📍 北辰·智汇谷 A座3楼路演厅</span>', '<span>' + s("pin", 16) + ' 北辰·智汇谷 A座3楼路演厅</span>', 1, "活动地点")
repn('<span>👥 已有23人报名</span>', '<span>' + s("users", 16) + ' 已有23人报名</span>', 1, "活动人数")
repn('                                💡 有数发现：', '                                有数发现：', 1, "有数发现")

# --- 我的页 ---
repn('<div class="profile-avatar">🏢</div>', '<div class="profile-avatar">' + s("company", 26) + '</div>', 1, "我的头像")
repn('<h4>🏷️ 企业档案</h4>', '<h4>' + s("tag", 16) + ' 企业档案</h4>', 1, "企业档案标题")
repn('<h4>📌 快速入口</h4>', '<h4>' + s("bolt", 16) + ' 快速入口</h4>', 1, "快速入口标题")
repn('<h4>⚙️ 设置</h4>', '<h4>' + s("settings", 16) + ' 设置</h4>', 1, "设置标题")
for emo, icon in [("📌", "flag"), ("📍", "pin"), ("🏭", "factory"), ("🎯", "target"),
                  ("💬", "chat"), ("⚠️", "alert"), ("📅", "calendar"),
                  ("🔔", "bell"), ("🌙", "moon"), ("🔄", "refresh")]:
    repn('<span class="pc-icon">%s</span>' % emo,
         '<span class="pc-icon">%s</span>' % s(icon, 18), 1, "我的页 " + icon)

# --- 顶栏 ---
repn('<span class="ch-title">🧑‍💼 智能管家</span>',
     '<span class="ch-title">' + s("spark", 18) + ' 智能管家</span>', 1, "管家标题")
repn('>✕</span>', '>' + s("close", 16) + '</span>', 2, "关闭按钮")

# --- 日历与时间轴 ---
repn('<div class="cal-filter">📅 ${m + 1}月', '<div class="cal-filter">${ic(\'calendar\', 16)} ${m + 1}月', 2, "日历筛选条")
repn('<span class="tl-from">📍 ${t.done', '<span class="tl-from">${ic(\'pin\', 16)} ${t.done', 1, "时间轴来源")

# --- 广场信息流 ---
repn('insight: "🤖 AI已识别：', 'insight: "管家已识别：', 2, "识别提示")
repn('text: "✅ 银行对公账户开好了', 'text: "银行对公账户开好了', 1, "我的小事完成态")
repn('<span>🔥 园区里有', '<span>${ic(\'bolt\', 16)} 园区里有', 1, "聚合提示")
repn("showToast('📅 已为你发起分享会需求')", "showToast('已为你发起分享会需求')", 1, "发起 toast")
repn('badge-thanks">🌸 感谢 · 送出心意</span>', 'badge-thanks">感谢 · 送出心意</span>', 1, "感谢徽章")
repn('<span class="rep-badge">🏆 被感谢', '<span class="rep-badge">${ic(\'trophy\', 14)} 被感谢', 1, "口碑徽章")
repn('<div class="thanks-token">🪙 系统打赏', '<div class="thanks-token">系统打赏', 1, "打赏")
repn('<span onclick="alsoHelped(${i})">👍 我也受过TA帮助', '<span onclick="alsoHelped(${i})">${ic(\'thumb\', 14)} 我也受过TA帮助', 1, "受过帮助")
repn('<span>💬 ${e.comments || 0}</span>', '<span>${ic(\'chat\', 14)} ${e.comments || 0}</span>', 1, "评论数1")
repn('<span style="color:#BE185D;">🌸 送TA一朵花</span>', '<span style="color:#BE185D;">${ic(\'heart\', 14)} 送TA一朵花</span>', 1, "送花")
repn("'<span class=\"privacy-lock\">🔒 仅自己可见</span>'", "'<span class=\"privacy-lock\">' + ic('lock', 14) + ' 仅自己可见</span>'", 1, "私密标")
repn("? '❓ 问题 · 求回答' : '📝 记录 · 已同步看板'", "? '问题 · 求回答' : '记录 · 已同步看板'", 1, "卡片类型徽章")
repn('<div class="answer-label">💬 园区伙伴回答</div>', '<div class="answer-label">${ic(\'chat\', 14)} 园区伙伴回答</div>', 1, "伙伴回答")
repn('<div class="private-footer">🔒 这条小事', '<div class="private-footer">${ic(\'lock\', 14)} 这条小事', 1, "私密脚注")
repn('<span>👍 ${e.likes}</span>', '<span>${ic(\'thumb\', 14)} ${e.likes}</span>', 1, "点赞数")
repn('<span>💬 ${e.comments}</span>', '<span>${ic(\'chat\', 14)} ${e.comments}</span>', 1, "评论数2")
repn("'<span>🔗 关联服务</span>'", "'<span>关联服务</span>'", 1, "关联服务")
repn("btn.textContent = '✓ 已报名';", "btn.textContent = '已报名';", 1, "已报名")
repn("showToast('✅ 报名成功，已同步到日程表');", "showToast('报名成功，已同步到日程表');", 1, "报名 toast")
repn("showToast('🌱 你也为 '", "showToast('你也为 '", 1, "口碑 toast")
repn('innerHTML = `📋 我的小事 <span', 'innerHTML = `${ic(\'book\', 16)} 我的小事 <span', 1, "我的小事标题")

# --- 补一个 14px 图标档 ---
repn('        .ic-16 { width: 16px; height: 16px; }',
     '        .ic-14 { width: 14px; height: 14px; }\n        .ic-16 { width: 16px; height: 16px; }', 1, "补 14px 图标档")

io.open(PATH, "w", encoding="utf-8").write(src)

# --- 断言：全文不再有象形 emoji ---
pat = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF✅❌⭐⚠⏰™®✓✕‍️]")
left = pat.findall(src)
if left:
    for i, l in enumerate(src.split("\n"), 1):
        if pat.search(l):
            print("残留", i, l.strip()[:140])
    sys.exit("还剩 %d 个 emoji，退出" % len(left))
print("第三趟完成，全文 emoji 归零")

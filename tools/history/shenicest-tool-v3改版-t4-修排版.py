# -*- coding: utf-8 -*-
"""第四趟：修 ev-generic 横幅少闭合 div 导致后续内容被 flex 容器横排的排版 bug，
改成 helper 函数生成，杜绝再漏。顺带修首页政策提醒卡的图标。"""
import io, sys

PATH = "/Users/qianhuizhao/work/research-system/9-references/shenicest黑客松-2026-08/shenicest-北辰-创业搭子-原型-2026-08-27.html"
src = io.open(PATH, encoding="utf-8").read()

def rep(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit("锚点[%s]命中 %d 次，应为 1 次，退出" % (label, n))
    src = src.replace(old, new, 1)
    print("  ok  %s" % label)

# helper：口径横幅统一由函数生成，闭合标签只写一次
rep("""        function ic(name, size) { return '<svg class="ic ic-' + (size || 18) + '"><use href="#i-' + name + '"></use></svg>'; }""",
    """        function ic(name, size) { return '<svg class="ic ic-' + (size || 18) + '"><use href="#i-' + name + '"></use></svg>'; }

        // 口径横幅：通用流程 / 演示内容 / 数据来源，闭合标签只在这一处写
        function evGeneric(title, desc) {
            return '<div class="ev-generic">' + ic('info', 18)
                 + '<div><div class="ev-generic-t">' + title + '</div>'
                 + '<div class="ev-generic-d">' + desc + '</div></div></div>';
        }""", "口径横幅 helper")

rep("""                h += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">通用流程口径，非政策原文</div>
                    <div class="ev-generic-d">这一类命题方数据库没有提供数据。下面只讲办事顺序，不写办理时限、费用和截止日期，一切以受理机关公告为准。</div>
                </div>`;""",
    """                h += evGeneric('通用流程口径，非政策原文',
                    '这一类命题方数据库没有提供数据。下面只讲办事顺序，不写办理时限、费用和截止日期，一切以受理机关公告为准。');""",
    "办事页通用流程横幅")

rep("""                h += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">园区名称来自命题方材料</div>
                    <div class="ev-generic-d">${d.parkNote}</div>
                </div>`;""",
    """                h += evGeneric('园区名称来自命题方材料', d.parkNote);""", "园区横幅")

rep("""                    h += `<div class="ev-generic">${ic('info', 18)}<div>
                        <div class="ev-generic-t">通用流程口径，非政策原文</div>
                        <div class="ev-generic-d">${d.genericNote}</div>
                    </div>`;""",
    """                    h += evGeneric('通用流程口径，非政策原文', d.genericNote);""", "混合页通用流程横幅")

rep("""            if (data.demo) {
                html += `<div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">演示内容，无命题方数据支撑</div>
                    <div class="ev-generic-d">这一页命题方数据库没有覆盖，内容用于演示交互，不作为办理依据。有真数据的是政策补贴、金融服务、融资机会，以及办事入口里的知识产权、找场地、招人。</div>
                </div>`;
            }""",
    """            if (data.demo) {
                html += evGeneric('演示内容，无命题方数据支撑',
                    '这一页命题方数据库没有覆盖，内容用于演示交互，不作为办理依据。有真数据的是政策补贴、金融服务、融资机会，以及办事入口里的知识产权、找场地、招人。');
            }""", "服务页演示横幅")

rep("""            document.getElementById('pageScroll').innerHTML = `
                <div class="ev-generic">${ic('info', 18)}<div>
                    <div class="ev-generic-t">日程为演示数据</div>
                    <div class="ev-generic-d">这里的日期用于演示小事引擎的写入与勾销，不来自命题方政策库或金融库，不作为申报或缴费依据。</div>
                </div>
                <div class="cal-card">""",
    """            document.getElementById('pageScroll').innerHTML = evGeneric('日程为演示数据',
                '这里的日期用于演示小事引擎的写入与勾销，不来自命题方政策库或金融库，不作为申报或缴费依据。') + `
                <div class="cal-card">""", "行政日历演示横幅")

# 首页政策提醒卡的图标与箭头
rep("""            el.innerHTML = `<span class="alert-icon">政策</span>""",
    """            el.innerHTML = `<span class="alert-icon">${ic('doc', 18)}</span>""", "政策提醒卡图标")
rep("""                <span class="alert-close">›</span>`;""",
    """                <span class="alert-close">${ic('chevron', 16)}</span>`;""", "政策提醒卡箭头")

# 管公司页里 section 标题与边界面板的左右边距归零（外层 .service-scroll 已有 20px padding）
rep("""        .cm-seg { display: flex;""",
    """        #cmBizPane .page-section-title, #cmBizPane .ev-panel, #cmBizPane .more-toggle { margin-left: 0; margin-right: 0; }
        .cm-seg { display: flex;""", "管公司页内边距")

# 清掉 serviceDetails 删除后留下的空注释
rep("""        // Service details data


""", "", "清空注释")

io.open(PATH, "w", encoding="utf-8").write(src)
print("第四趟完成")

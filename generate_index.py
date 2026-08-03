#!/usr/bin/env python3
"""从 archive/ 目录重新生成 index.html：最新一期入口 + 往期内容列表。"""
import re
from pathlib import Path

ARCHIVE_ROOT = Path("archive")


def find_days():
    days = []
    for p in ARCHIVE_ROOT.glob("*/day-*.html"):
        m = re.match(r"day-(\d{4}-\d{2}-\d{2})\.html$", p.name)
        if m:
            days.append((m.group(1), p))
    return sorted(days, key=lambda item: item[0], reverse=True)


def display_date(d):
    y, m, day = d.split("-")
    return f"{y} 年 {int(m)} 月 {int(day)} 日"


def build_html(days):
    latest_date, _ = days[0]
    compact_date = latest_date.replace("-", "")
    display = display_date(latest_date)

    history_items = "".join(
        f'<li><a href="{path.as_posix()}">{display_date(d)}</a></li>'
        for d, path in days[1:]
    )
    history_html = (
        f'<div class="history"><div class="history-title">往期内容</div><ul>{history_items}</ul></div>'
        if history_items
        else ""
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>每日英文阅读练习</title>
  <style>
    *,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ min-height:100vh; font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;
      background:#f2f2f7; display:flex; align-items:center; justify-content:center; padding:32px 16px; }}
    .card {{ max-width:400px; width:100%; background:#fff; border-radius:28px; overflow:hidden;
      box-shadow:0 4px 24px rgba(0,0,0,.08), 0 1px 4px rgba(0,0,0,.04); }}
    .header {{ background:#111; color:#fff; padding:28px 28px 26px; }}
    .badge {{ display:inline-block; background:rgba(255,255,255,.12); color:rgba(255,255,255,.8);
      font-size:11px; font-weight:600; letter-spacing:.1em; padding:3px 10px; border-radius:20px;
      margin-bottom:14px; text-transform:uppercase; }}
    .title {{ font-size:26px; font-weight:800; line-height:1.2; }}
    .subtitle {{ margin-top:8px; font-size:14px; color:rgba(255,255,255,.55); line-height:1.5; }}
    .body {{ padding:22px 28px 28px; }}
    .btn {{ display:block; padding:15px; background:#111; color:#fff; text-decoration:none;
      text-align:center; font-weight:700; font-size:15px; border-radius:14px; margin-bottom:16px; }}
    .footer {{ text-align:center; color:#bbb; font-size:12px; line-height:1.8; }}
    .footer strong {{ color:#777; }}
    .history {{ margin-top:18px; padding-top:14px; border-top:1px solid #f0f0f0; }}
    .history-title {{ font-size:12px; color:#999; font-weight:600; margin-bottom:8px; }}
    .history ul {{ list-style:none; max-height:220px; overflow-y:auto; }}
    .history li {{ padding:6px 0; border-bottom:1px solid #f7f7f9; }}
    .history li:last-child {{ border-bottom:none; }}
    .history a {{ font-size:13px; color:#06c; text-decoration:none; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="badge">Daily Reading</div>
      <div class="title">每日英文阅读练习</div>
      <div class="subtitle">每天10分钟，贴近生活的小故事 + 生词 + 理解题 + 写作</div>
    </div>
    <div class="body">
      <a class="btn" href="./latest.html?t={compact_date}">开始今天的练习</a>
      <div class="footer">
        最新一期：<strong>{display}</strong><br>
        做完记得点页面底部的难度反馈按钮
      </div>
      {history_html}
    </div>
  </div>
</body>
</html>
"""


def main():
    days = find_days()
    if not days:
        print("No archived days found, nothing to do")
        return
    Path("index.html").write_text(build_html(days), encoding="utf-8")
    print(f"OK: index.html regenerated, latest={days[0][0]}, {len(days) - 1} past entries listed")


if __name__ == "__main__":
    main()

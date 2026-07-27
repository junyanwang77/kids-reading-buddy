#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Current directory:"
pwd

reading_date="${1:-$(date +%F)}"

if ! [[ "$reading_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "Invalid date: $reading_date"
  exit 1
fi

echo "Publishing reading date: $reading_date"

day_html="day-${reading_date}.html"
day_json="day-${reading_date}.json"

if [ ! -f "$day_html" ]; then
  echo "Expected HTML file not found: $day_html"
  exit 1
fi

if [ ! -f "$day_json" ]; then
  echo "Expected JSON file not found: $day_json"
  exit 1
fi

echo "Updating latest files..."
cp "$day_html" latest.html
cp "$day_json" latest.json

archive_dir="archive/${reading_date:0:7}"
echo "Archiving dated files into $archive_dir..."
mkdir -p "$archive_dir"
mv -f "$day_html" "$archive_dir/"
mv -f "$day_json" "$archive_dir/"

compact_date=$(echo "$reading_date" | tr -d '-')
display_year="${reading_date:0:4}"
display_month="${reading_date:5:2}"
display_day="${reading_date:8:2}"
display_date="${display_year} 年 ${display_month#0} 月 ${display_day#0} 日"

echo "Updating index.html to published date: $reading_date"

cat > index.html <<HTML
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>每日英文阅读练习</title>
  <style>
    *,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
    body { min-height:100vh; font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;
      background:#f2f2f7; display:flex; align-items:center; justify-content:center; padding:32px 16px; }
    .card { max-width:400px; width:100%; background:#fff; border-radius:28px; overflow:hidden;
      box-shadow:0 4px 24px rgba(0,0,0,.08), 0 1px 4px rgba(0,0,0,.04); }
    .header { background:#111; color:#fff; padding:28px 28px 26px; }
    .badge { display:inline-block; background:rgba(255,255,255,.12); color:rgba(255,255,255,.8);
      font-size:11px; font-weight:600; letter-spacing:.1em; padding:3px 10px; border-radius:20px;
      margin-bottom:14px; text-transform:uppercase; }
    .title { font-size:26px; font-weight:800; line-height:1.2; }
    .subtitle { margin-top:8px; font-size:14px; color:rgba(255,255,255,.55); line-height:1.5; }
    .body { padding:22px 28px 28px; }
    .btn { display:block; padding:15px; background:#111; color:#fff; text-decoration:none;
      text-align:center; font-weight:700; font-size:15px; border-radius:14px; margin-bottom:16px; }
    .footer { text-align:center; color:#bbb; font-size:12px; line-height:1.8; }
    .footer strong { color:#777; }
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
      <a class="btn" href="./latest.html?t=$compact_date">开始今天的练习</a>
      <div class="footer">
        最新一期：<strong>$display_date</strong><br>
        做完记得点页面底部的难度反馈按钮
      </div>
    </div>
  </div>
</body>
</html>
HTML

echo "Git status before commit:"
git status --short

git add .

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

commit_msg="Publish reading $reading_date"
git commit -m "$commit_msg"
git push

echo "Published successfully."

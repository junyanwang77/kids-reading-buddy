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

echo "Archiving today's audio into $archive_dir..."
for audio_file in "story-${reading_date}.mp3" word-"${reading_date}"-*.mp3; do
  if [ -f "$audio_file" ]; then
    cp "$audio_file" "$archive_dir/"
  fi
done

echo "Updating index.html to published date: $reading_date"

python3 generate_index.py

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

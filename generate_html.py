#!/usr/bin/env python3
"""把 day-YYYY-MM-DD.json 转成当天的阅读练习网页 day-YYYY-MM-DD.html。"""
import json
import sys
import html
from pathlib import Path

REPO = "junyanwang77/kids-english-daily"
FEEDBACK_TAGS = ["太简单", "正合适", "太难", "生词过多", "内容感兴趣"]


def esc(s):
    return html.escape(s, quote=True)


def issue_url(date, tag):
    title = f"反馈:{tag} ({date})"
    body = f"日期: {date}\n标签: {tag}\n\n（如果有补充想法，可以写在这里，提交后系统会自动读取并调整难度）"
    from urllib.parse import quote
    return (
        f"https://github.com/{REPO}/issues/new"
        f"?title={quote(title)}&labels=feedback,{quote(tag)}&body={quote(body)}"
    )


def build_html(data):
    date = data["date"]
    difficulty = data.get("difficulty", "?")
    story_title = esc(data["story_title"])
    story_text = esc(data["story_text"])

    vocab_html = "".join(
        f'<li><b>{esc(v["word"])}</b> {esc(v["meaning_cn"])} '
        f'<div class="ex">{esc(v["example"])}</div></li>'
        for v in data["vocabulary"]
    )
    comp_html = "".join(f"<li>{esc(q)}</li>" for q in data["comprehension_questions"])
    speak_html = "".join(f"<li>{esc(q)}</li>" for q in data["speaking_questions"])
    scaffold_html = "".join(f"<li>{esc(s)}</li>" for s in data["writing_task"]["scaffold"])
    observe_html = "".join(
        f'<li><label><input type="checkbox"> {esc(o)}</label></li>'
        for o in data["parent_observation"]
    )
    feedback_html = "".join(
        f'<a class="fbtn" target="_blank" href="{issue_url(date, tag)}">{tag}</a>'
        for tag in FEEDBACK_TAGS
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(story_title)} · 英文阅读练习</title>
<style>
  *,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif; background:#f2f2f7; padding:20px 14px 60px; color:#222; }}
  .wrap {{ max-width:560px; margin:0 auto; }}
  .badge {{ display:inline-block; background:#111; color:#fff; font-size:12px; padding:3px 10px; border-radius:20px; margin-bottom:10px; }}
  h1 {{ font-size:22px; margin-bottom:6px; }}
  .meta {{ color:#888; font-size:13px; margin-bottom:18px; }}
  section {{ background:#fff; border-radius:16px; padding:18px 20px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,.05); }}
  section h2 {{ font-size:15px; color:#555; margin-bottom:10px; }}
  .story {{ font-size:16px; line-height:1.8; white-space:pre-wrap; }}
  .readbtn {{ display:inline-block; margin-top:12px; padding:8px 16px; background:#0a7; color:#fff; border:none; border-radius:10px; font-size:14px; }}
  ul {{ list-style:none; }}
  ul li {{ padding:8px 0; border-bottom:1px solid #f0f0f0; font-size:14px; line-height:1.6; }}
  ul li:last-child {{ border-bottom:none; }}
  .ex {{ color:#888; font-size:13px; margin-top:2px; }}
  .fb-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .fbtn {{ flex:1 1 auto; text-align:center; padding:10px 6px; background:#111; color:#fff; border-radius:10px; text-decoration:none; font-size:13px; font-weight:600; }}
  .hint {{ font-size:12px; color:#999; margin-top:10px; line-height:1.6; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="badge">难度 {difficulty} / 5</div>
  <h1>{story_title}</h1>
  <div class="meta">{esc(date)} 的阅读练习</div>

  <section>
    <h2>1. 短文 / 朗读版本</h2>
    <div class="story" id="storyText">{story_text}</div>
    <button class="readbtn" onclick="readStory()">🔊 点击朗读</button>
  </section>

  <section>
    <h2>2. 生词解释</h2>
    <ul>{vocab_html}</ul>
  </section>

  <section>
    <h2>3. 阅读理解题</h2>
    <ul>{comp_html}</ul>
  </section>

  <section>
    <h2>4. 口语问答（说出来，不用写）</h2>
    <ul>{speak_html}</ul>
  </section>

  <section>
    <h2>5. 三句话写作</h2>
    <p style="font-size:14px;margin-bottom:8px;">{esc(data['writing_task']['prompt'])}</p>
    <ul>{scaffold_html}</ul>
  </section>

  <section>
    <h2>6. 家长观察记录</h2>
    <ul>{observe_html}</ul>
  </section>

  <section>
    <h2>7. 今天难度怎么样？（点一下，跳到 GitHub 提交，系统会自动调整明天难度）</h2>
    <div class="fb-row">{feedback_html}</div>
    <div class="hint">点击后会打开 GitHub 新建 Issue 的页面，内容已经帮你填好，直接点绿色的"Submit new issue"按钮就完成了。</div>
  </section>
</div>
<script>
function readStory() {{
  var text = document.getElementById('storyText').innerText;
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US';
  u.rate = 0.9;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}}
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_html.py YYYY-MM-DD")
        sys.exit(1)
    date = sys.argv[1]
    src = Path(f"day-{date}.json")
    if not src.exists():
        print(f"Missing input file: {src}")
        sys.exit(1)
    data = json.loads(src.read_text(encoding="utf-8"))
    out = Path(f"day-{date}.html")
    out.write_text(build_html(data), encoding="utf-8")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()

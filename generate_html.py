#!/usr/bin/env python3
"""把 day-YYYY-MM-DD.json 转成当天的阅读练习网页 day-YYYY-MM-DD.html。"""
import json
import sys
import html
from pathlib import Path

REPO = "junyanwang77/kids-reading-buddy"
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


def known_word_url(date, word):
    title = f"已认识:{word} ({date})"
    body = (
        f"单词: {word}\n日期: {date}\n\n"
        "（点这个是告诉系统这个词孩子已经认识了，以后生成新内容时不会再把它当成生词。"
        "提交后不用做别的事。）"
    )
    from urllib.parse import quote
    return (
        f"https://github.com/{REPO}/issues/new"
        f"?title={quote(title)}&labels=known-word&body={quote(body)}"
    )


def build_html(data):
    date = data["date"]
    difficulty = data.get("difficulty", "?")
    story_title = esc(data["story_title"])
    story_text = esc(data["story_text"])

    def vocab_item(v):
        pos_html = f' <span class="pos">{esc(v["pos"])}</span>' if v.get("pos") else ""
        ipa_html = f' <span class="ipa">/{esc(v["ipa"])}/</span>' if v.get("ipa") else ""
        audio_html = (
            f'<audio controls preload="none" src="{esc(v["audio"])}"></audio>'
            if v.get("audio")
            else ""
        )
        return (
            f'<li><b>{esc(v["word"])}</b>{pos_html}{ipa_html} {esc(v["meaning_cn"])}'
            f'{audio_html}'
            f'<div class="ex">{esc(v["example"])}</div>'
            f'<a class="knownbtn" target="_blank" href="{known_word_url(date, v["word"])}">✓ TA已认识，别再列了</a>'
            f'</li>'
        )

    def speak_item(idx, q):
        return f"""<li>
      <div class="q-text">{esc(q)}</div>
      <div class="recorder" data-idx="{idx}">
        <button class="recbtn" onclick="toggleRecord(this)">🎤 录音</button>
        <audio class="rec-playback" controls style="display:none;"></audio>
        <a class="rec-download" style="display:none;">⬇ 保存录音</a>
      </div>
    </li>"""

    vocab_html = "".join(vocab_item(v) for v in data["vocabulary"])
    comp_html = "".join(f"<li>{esc(q)}</li>" for q in data["comprehension_questions"])
    speak_html = "".join(speak_item(i, q) for i, q in enumerate(data["speaking_questions"]))
    def write_item(idx, s):
        return f"""<li>
      <div class="q-text">{esc(s)}</div>
      <textarea class="write-box" data-idx="{idx}" rows="2" placeholder="在这里写第 {idx + 1} 句..."></textarea>
    </li>"""

    scaffold_html = "".join(write_item(i, s) for i, s in enumerate(data["writing_task"]["scaffold"]))
    observe_html = "".join(
        f'<li><label><input type="checkbox"> {esc(o)}</label></li>'
        for o in data["parent_observation"]
    )
    feedback_html = "".join(
        f'<a class="fbtn" target="_blank" href="{issue_url(date, tag)}">{tag}</a>'
        for tag in FEEDBACK_TAGS
    )

    if data.get("story_audio"):
        story_audio_html = (
            f'<audio class="story-audio" controls preload="none" src="{esc(data["story_audio"])}"></audio>'
            f'<div class="fallback-hint">上面播放不了的话，可以点这个备用朗读（用的是手机/电脑自带的朗读功能，效果没有上面的好）：</div>'
            f'<button class="readbtn" onclick="readStory()">🔊 备用朗读</button>'
        )
    else:
        story_audio_html = '<button class="readbtn" onclick="readStory()" style="background:#0a7;color:#fff;border:none;">🔊 点击朗读</button>'

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
  audio {{ width:100%; }}
  section h2 {{ font-size:15px; color:#555; margin-bottom:10px; }}
  .story {{ font-size:16px; line-height:1.8; white-space:pre-wrap; }}
  .story-audio {{ width:100%; margin-top:12px; }}
  .readbtn {{ display:inline-block; margin-top:10px; padding:6px 14px; background:none; color:#999; border:1px solid #ddd; border-radius:10px; font-size:12px; }}
  .fallback-hint {{ font-size:12px; color:#aaa; margin-top:4px; }}
  ul {{ list-style:none; }}
  ul li {{ padding:8px 0; border-bottom:1px solid #f0f0f0; font-size:14px; line-height:1.6; }}
  ul li:last-child {{ border-bottom:none; }}
  ul li audio {{ display:block; height:32px; margin-top:4px; max-width:220px; }}
  .pos {{ color:#0a7; font-size:12px; font-style:italic; }}
  .ipa {{ color:#888; font-size:13px; }}
  .ex {{ color:#888; font-size:13px; margin-top:2px; }}
  .write-box {{ width:100%; margin-top:6px; padding:8px 10px; font-size:14px; font-family:inherit; border:1px solid #ddd; border-radius:8px; resize:vertical; }}
  .write-actions {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:12px; }}
  .savebtn {{ padding:8px 16px; background:#0a7; color:#fff; border:none; border-radius:10px; font-size:13px; font-weight:600; }}
  .write-download {{ font-size:12px; color:#06c; text-decoration:none; }}
  .write-status {{ font-size:12px; color:#0a7; }}
  .knownbtn {{ display:inline-block; margin-top:6px; padding:4px 10px; background:#f2f2f7; color:#06c; border-radius:8px; text-decoration:none; font-size:12px; }}
  .fb-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .fbtn {{ flex:1 1 auto; text-align:center; padding:10px 6px; background:#111; color:#fff; border-radius:10px; text-decoration:none; font-size:13px; font-weight:600; }}
  .hint {{ font-size:12px; color:#999; margin-top:10px; line-height:1.6; }}
  .q-text {{ margin-bottom:6px; }}
  .recorder {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; }}
  .recbtn {{ padding:6px 14px; background:#f2f2f7; color:#333; border:1px solid #ddd; border-radius:10px; font-size:12px; }}
  .recbtn.recording {{ background:#e33; color:#fff; border-color:#e33; }}
  .rec-playback {{ width:100%; height:32px; margin-top:2px; }}
  .rec-download {{ font-size:12px; color:#06c; text-decoration:none; }}
  .rec-hint {{ font-size:12px; color:#aaa; margin-top:10px; line-height:1.6; }}
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
    {story_audio_html}
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
    <div class="rec-hint">点"🎤 录音"可以把孩子的回答录下来当场回放；觉得满意的话点"保存录音"下载到本设备（录音不会自动上传，只存在这台手机/电脑上）。</div>
  </section>

  <section>
    <h2>5. 三句话写作</h2>
    <p style="font-size:14px;margin-bottom:8px;">{esc(data['writing_task']['prompt'])}</p>
    <ul id="writeList">{scaffold_html}</ul>
    <div class="write-actions">
      <button class="savebtn" onclick="saveWriting()">💾 保存写作</button>
      <a class="write-download" id="writeDownload" style="display:none;">⬇ 下载留档</a>
      <span class="write-status" id="writeStatus"></span>
    </div>
    <div class="rec-hint">写的时候会自动存在这台设备上，换个时间打开也还在；点"保存写作"能生成一份文本文件下载留档。</div>
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
var speaking = false;

function updateReadBtns() {{
  document.querySelectorAll('.readbtn').forEach(function(b) {{
    if (!b.dataset.orig) b.dataset.orig = b.textContent;
    b.textContent = speaking ? '⏹ 停止朗读' : b.dataset.orig;
  }});
}}

function readStory() {{
  if (speaking) {{
    window.speechSynthesis.cancel();
    speaking = false;
    updateReadBtns();
    return;
  }}
  var text = document.getElementById('storyText').innerText;
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US';
  u.rate = 0.9;
  u.onend = function() {{ speaking = false; updateReadBtns(); }};
  u.onerror = function() {{ speaking = false; updateReadBtns(); }};
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
  speaking = true;
  updateReadBtns();
}}

var activeRecorders = {{}};
var STORY_DATE = {date!r};

async function toggleRecord(btn) {{
  var wrap = btn.closest('.recorder');
  var idx = wrap.dataset.idx;

  if (activeRecorders[idx]) {{
    activeRecorders[idx].stop();
    return;
  }}

  if (!navigator.mediaDevices || !window.MediaRecorder) {{
    alert('这个浏览器不支持录音功能，换个浏览器（比如手机自带的浏览器）试试。');
    return;
  }}

  try {{
    var stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
    var mr = new MediaRecorder(stream);
    var chunks = [];
    mr.ondataavailable = function(e) {{ if (e.data.size > 0) chunks.push(e.data); }};
    mr.onstop = function() {{
      var blob = new Blob(chunks, {{ type: mr.mimeType || 'audio/webm' }});
      var url = URL.createObjectURL(blob);
      var audioEl = wrap.querySelector('.rec-playback');
      audioEl.src = url;
      audioEl.style.display = 'block';
      var ext = (mr.mimeType || '').indexOf('mp4') !== -1 ? 'm4a' : 'webm';
      var dl = wrap.querySelector('.rec-download');
      dl.href = url;
      dl.download = 'speaking-' + (parseInt(idx, 10) + 1) + '-' + STORY_DATE + '.' + ext;
      dl.style.display = 'inline-block';
      stream.getTracks().forEach(function(t) {{ t.stop(); }});
      btn.textContent = '🎤 重新录音';
      btn.classList.remove('recording');
      delete activeRecorders[idx];
    }};
    mr.start();
    activeRecorders[idx] = mr;
    btn.textContent = '⏹ 停止录音';
    btn.classList.add('recording');
  }} catch (err) {{
    alert('没能打开麦克风，请检查浏览器是否有录音权限。');
  }}
}}

var WRITE_KEY = 'writing-' + STORY_DATE;

function restoreWriting() {{
  var saved;
  try {{ saved = JSON.parse(localStorage.getItem(WRITE_KEY) || '[]'); }} catch (e) {{ saved = []; }}
  document.querySelectorAll('.write-box').forEach(function(box) {{
    var idx = parseInt(box.dataset.idx, 10);
    if (saved[idx]) box.value = saved[idx];
    box.addEventListener('input', function() {{
      var values = [];
      document.querySelectorAll('.write-box').forEach(function(b) {{ values[parseInt(b.dataset.idx, 10)] = b.value; }});
      localStorage.setItem(WRITE_KEY, JSON.stringify(values));
    }});
  }});
}}
restoreWriting();

function saveWriting() {{
  var values = [];
  document.querySelectorAll('.write-box').forEach(function(b) {{ values[parseInt(b.dataset.idx, 10)] = b.value; }});
  localStorage.setItem(WRITE_KEY, JSON.stringify(values));
  var text = values.map(function(v, i) {{ return (i + 1) + '. ' + (v || ''); }}).join('\\n');
  var blob = new Blob([text], {{ type: 'text/plain' }});
  var url = URL.createObjectURL(blob);
  var dl = document.getElementById('writeDownload');
  dl.href = url;
  dl.download = 'writing-' + STORY_DATE + '.txt';
  dl.style.display = 'inline-block';
  dl.click();
  var status = document.getElementById('writeStatus');
  status.textContent = '已保存 ✓';
  setTimeout(function() {{ status.textContent = ''; }}, 2000);
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

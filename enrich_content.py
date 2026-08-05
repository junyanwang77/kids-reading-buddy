#!/usr/bin/env python3
"""给当天内容包补充标准发音音频（edge-tts）和生词音标（eng-to-ipa）。

失败时不中断整体流程：某个词/某段音频合成失败只跳过，不影响其余内容照常发布。
"""
import asyncio
import glob
import json
import os
import sys
from pathlib import Path

import edge_tts
import eng_to_ipa as ipa

VOICE = "en-US-JennyNeural"
RATE = "-10%"


async def synth(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(out_path))


def cleanup_old_audio():
    for f in glob.glob("story-*.mp3") + glob.glob("word-*.mp3"):
        os.remove(f)


def main():
    if len(sys.argv) != 2:
        print("Usage: enrich_content.py YYYY-MM-DD")
        sys.exit(1)
    date = sys.argv[1]
    path = Path(f"day-{date}.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    cleanup_old_audio()

    # 文件名按日期命名（而不是通用的 story.mp3/word-N.mp3），这样发布时能连同当天的
    # html/json 一起原样归档进 archive/YYYY-MM/，往期页面不会在第二天被新内容覆盖掉。
    story_audio_path = Path(f"story-{date}.mp3")
    try:
        asyncio.run(synth(data["story_text"], story_audio_path))
        data["story_audio"] = story_audio_path.name
        print(f"OK: {story_audio_path} generated")
    except Exception as e:
        print(f"WARN: story audio generation failed, will fall back to browser TTS: {e}")

    for i, item in enumerate(data["vocabulary"]):
        word = item["word"]
        try:
            item["ipa"] = ipa.convert(word)
        except Exception as e:
            print(f"WARN: ipa lookup for '{word}' failed: {e}")

        try:
            audio_path = Path(f"word-{date}-{i}.mp3")
            asyncio.run(synth(word, audio_path))
            item["audio"] = audio_path.name
        except Exception as e:
            print(f"WARN: audio for '{word}' failed: {e}")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Enriched {path}")


if __name__ == "__main__":
    main()

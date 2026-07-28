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
    for f in glob.glob("story.mp3") + glob.glob("word-*.mp3"):
        os.remove(f)


def main():
    if len(sys.argv) != 2:
        print("Usage: enrich_content.py YYYY-MM-DD")
        sys.exit(1)
    date = sys.argv[1]
    path = Path(f"day-{date}.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    cleanup_old_audio()

    try:
        asyncio.run(synth(data["story_text"], Path("story.mp3")))
        data["story_audio"] = "story.mp3"
        print("OK: story.mp3 generated")
    except Exception as e:
        print(f"WARN: story audio generation failed, will fall back to browser TTS: {e}")

    for i, item in enumerate(data["vocabulary"]):
        word = item["word"]
        try:
            item["ipa"] = ipa.convert(word)
        except Exception as e:
            print(f"WARN: ipa lookup for '{word}' failed: {e}")

        try:
            audio_path = Path(f"word-{i}.mp3")
            asyncio.run(synth(word, audio_path))
            item["audio"] = audio_path.name
        except Exception as e:
            print(f"WARN: audio for '{word}' failed: {e}")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Enriched {path}")


if __name__ == "__main__":
    main()

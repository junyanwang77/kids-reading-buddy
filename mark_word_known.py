#!/usr/bin/env python3
"""把家长在手机端标记为"已认识"的生词，写入 profile.json 的 assessment.known_extra_words。"""
import json
import sys
from pathlib import Path

PROFILE_PATH = Path("profile.json")


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print("Usage: mark_word_known.py <word>")
        sys.exit(1)

    word = sys.argv[1].strip().lower()
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    known = profile.setdefault("assessment", {}).setdefault("known_extra_words", [])

    if word in known:
        print(f"'{word}' already in known_extra_words, nothing to do")
        return

    known.append(word)
    PROFILE_PATH.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Added '{word}' to known_extra_words")


if __name__ == "__main__":
    main()

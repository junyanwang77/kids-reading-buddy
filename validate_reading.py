#!/usr/bin/env python3
"""检查当天生成的内容包是否完整、结构正确。"""
import csv
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "date", "difficulty", "story_title", "story_text",
    "vocabulary", "comprehension_questions", "speaking_questions",
    "writing_task", "parent_observation",
]

CEFR_CSV_PATH = Path("data/cefrj-vocabulary-profile.csv")
PROFILE_PATH = Path("profile.json")
CEFR_ORDER = ["A1", "A2", "B1", "B2"]

# difficulty (1-5) -> 已知词区间，跟 profile.json 的 state.difficulty_scale 保持一致
DIFFICULTY_KNOWN_LEVELS = {
    1: {"A1"},
    2: {"A1", "A2"},
    3: {"A1", "A2"},
    4: {"A1", "A2", "B1"},
    5: {"A1", "A2", "B1", "B2"},
}


def load_cefr_levels(csv_path):
    """headword(小写) -> 该词在词表里出现过的最简单 CEFR 等级。"""
    if not csv_path.exists():
        return {}
    levels = {}
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            word = row.get("headword", "").strip().lower()
            cefr = row.get("CEFR", "").strip().upper()
            if not word or cefr not in CEFR_ORDER:
                continue
            if word not in levels or CEFR_ORDER.index(cefr) < CEFR_ORDER.index(levels[word]):
                levels[word] = cefr
    return levels


def check_vocab_coverage(data):
    """阻断检查：story_text 里如果有明显超出已知词区间、又没被列进生词表的词，直接判失败。"""
    known_levels = DIFFICULTY_KNOWN_LEVELS.get(data.get("difficulty"))
    if known_levels is None:
        return
    cefr_levels = load_cefr_levels(CEFR_CSV_PATH)
    if not cefr_levels:
        return

    known_extra_words = set()
    if PROFILE_PATH.exists():
        profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        known_extra_words = {
            w.strip().lower() for w in profile.get("assessment", {}).get("known_extra_words", [])
        }

    vocab_words = {v["word"].strip().lower() for v in data.get("vocabulary", []) if v.get("word")}
    story_words = {w.lower() for w in re.findall(r"\b[a-zA-Z']+\b", data.get("story_text", ""))}

    missing = []
    for word in sorted(story_words - vocab_words - known_extra_words):
        cefr = cefr_levels.get(word)
        if cefr and cefr not in known_levels:
            missing.append((word, cefr))

    if missing:
        for word, cefr in missing:
            print(f"FAIL: '{word}' is CEFR {cefr}, above known band {sorted(known_levels)} "
                  f"for difficulty {data['difficulty']}, but not listed in vocabulary")
        sys.exit(1)


def check_json_content(data, json_path):
    for key in REQUIRED_KEYS:
        if key not in data:
            print(f"FAIL: {json_path} missing key '{key}'")
            sys.exit(1)

    if not data["story_text"].strip():
        print("FAIL: story_text is empty")
        sys.exit(1)
    if len(data["vocabulary"]) == 0:
        print("FAIL: vocabulary is empty")
        sys.exit(1)
    if len(data["comprehension_questions"]) < 3:
        print("FAIL: fewer than 3 comprehension questions")
        sys.exit(1)

    check_vocab_coverage(data)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_reading.py YYYY-MM-DD [--json-only]")
        sys.exit(1)
    date = sys.argv[1]
    json_only = "--json-only" in sys.argv[2:]

    json_path = Path(f"day-{date}.json")
    if not json_path.exists():
        print(f"FAIL: missing {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    check_json_content(data, json_path)

    if json_only:
        print(f"OK: {json_path} looks valid")
        return

    html_path = Path(f"day-{date}.html")
    if not html_path.exists():
        print(f"FAIL: missing {html_path}")
        sys.exit(1)

    print(f"OK: {json_path} and {html_path} look valid")


if __name__ == "__main__":
    main()

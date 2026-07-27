#!/usr/bin/env python3
"""检查当天生成的内容包是否完整、结构正确。"""
import json
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "date", "difficulty", "story_title", "story_text",
    "vocabulary", "comprehension_questions", "speaking_questions",
    "writing_task", "parent_observation",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_reading.py YYYY-MM-DD")
        sys.exit(1)
    date = sys.argv[1]

    json_path = Path(f"day-{date}.json")
    html_path = Path(f"day-{date}.html")

    if not json_path.exists():
        print(f"FAIL: missing {json_path}")
        sys.exit(1)
    if not html_path.exists():
        print(f"FAIL: missing {html_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
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

    print(f"OK: {json_path} and {html_path} look valid")


if __name__ == "__main__":
    main()

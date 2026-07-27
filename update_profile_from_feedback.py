#!/usr/bin/env python3
"""根据家长在 GitHub Issue 里提交的反馈标签，调整 profile.json 里的难度状态。"""
import json
import sys
from datetime import date
from pathlib import Path

VALID_TAGS = ["太简单", "正合适", "太难", "生词过多", "内容感兴趣"]
PROFILE_PATH = Path("profile.json")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in VALID_TAGS:
        print(f"Usage: update_profile_from_feedback.py <{'|'.join(VALID_TAGS)}> [YYYY-MM-DD]")
        sys.exit(1)

    tag = sys.argv[1]
    feedback_date = sys.argv[2] if len(sys.argv) > 2 else date.today().isoformat()

    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    state = profile["state"]

    difficulty_before = state["current_difficulty"]
    vocab_before = state["vocab_count_target"]

    if tag == "太简单":
        state["current_difficulty"] = min(5, difficulty_before + 1)
    elif tag == "太难":
        state["current_difficulty"] = max(1, difficulty_before - 1)
    elif tag == "生词过多":
        state["vocab_count_target"] = max(3, vocab_before - 2)
    # 正合适 / 内容感兴趣：不调整难度和生词量，只记录历史

    state["last_updated"] = feedback_date

    profile.setdefault("history", []).append({
        "date": feedback_date,
        "feedback": tag,
        "difficulty_before": difficulty_before,
        "difficulty_after": state["current_difficulty"],
        "vocab_count_before": vocab_before,
        "vocab_count_after": state["vocab_count_target"],
    })

    PROFILE_PATH.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"Updated profile: difficulty {difficulty_before}->{state['current_difficulty']}, "
        f"vocab_count_target {vocab_before}->{state['vocab_count_target']}"
    )


if __name__ == "__main__":
    main()

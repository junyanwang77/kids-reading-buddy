# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A personalized daily English reading-practice generator for one specific child (age 11, Shenzhen public-school grade 6 level — see `profile.json`). A GitHub Actions workflow generates a story + vocabulary + comprehension/speaking/writing tasks each day, adds pronunciation audio and IPA, renders it to a mobile HTML page, and publishes it. Two more workflows close the loop from the page, entirely from a phone: the parent submits a difficulty-feedback tag, which becomes a GitHub Issue that automatically adjusts `profile.json` for the next day's generation; and next to each vocabulary word, the parent can tap "already known" to mark that specific word as known, via the same pre-filled-Issue mechanism.

## Commands

Generate today's content package locally (same command the workflow runs):

```bash
claude -p "$(cat prompts/daily_reading.md)" \
  --model sonnet \
  --permission-mode bypassPermissions \
  --allowedTools "Read,Write"
```

Then run the rest of the pipeline manually, in order:

```bash
pip install --quiet edge-tts eng-to-ipa      # once, if not already installed
python3 enrich_content.py YYYY-MM-DD          # adds story.mp3 / word-N.mp3 / IPA
python3 generate_html.py YYYY-MM-DD           # renders day-YYYY-MM-DD.html
python3 validate_reading.py YYYY-MM-DD        # must pass before publishing
bash ./publish.sh [YYYY-MM-DD]                # defaults to today
```

Apply a parent feedback tag manually (normally done by `handle-feedback.yml` from a GitHub Issue label):

```bash
python3 update_profile_from_feedback.py <太简单|正合适|太难|生词过多|内容感兴趣> [YYYY-MM-DD]
```

Mark a specific word as known manually (normally done by `handle-known-word.yml` from a GitHub Issue opened via the page's per-word "✓ TA已认识" link):

```bash
python3 mark_word_known.py <word>
```

There is no build step, package manager, or lint/test framework — `validate_reading.py` is the correctness check that stands in for tests.

## Architecture

Three independent workflows:

```
.github/workflows/daily-reading.yml (workflow_dispatch only — no cron yet)
        │  skips entirely if archive/YYYY-MM/day-YYYY-MM-DD.json already exists
        ▼
claude -p prompts/daily_reading.md   →  day-YYYY-MM-DD.json  (reads profile.json for personalization)
        │
        ▼
python3 enrich_content.py YYYY-MM-DD →  adds story.mp3, word-N.mp3 (edge-tts) and IPA per vocab word
        │
        ▼
python3 generate_html.py YYYY-MM-DD  →  day-YYYY-MM-DD.html
        │
        ▼
python3 validate_reading.py YYYY-MM-DD →  fails the run if required JSON keys/content are missing
        │
        ▼
bash publish.sh YYYY-MM-DD           →  updates latest.html/latest.json, moves dated files into
                                         archive/YYYY-MM/, regenerates index.html, commits + pushes
```

```
.github/workflows/handle-feedback.yml (triggered by a new Issue labeled "feedback")
        │  the reading page's feedback buttons pre-fill and open a GitHub Issue
        ▼
update_profile_from_feedback.py <tag> →  adjusts profile.json state.current_difficulty /
                                          state.vocab_count_target, appends to profile.json history
        │
        ▼
commits profile.json, comments on the Issue, closes it
```

```
.github/workflows/handle-known-word.yml (triggered by a new Issue labeled "known-word")
        │  each vocab word on the reading page has a "✓ TA已认识" link that pre-fills and opens a GitHub Issue
        ▼
mark_word_known.py <word>            →  appends word (lowercased, deduped) to
                                          profile.json assessment.known_extra_words
        │
        ▼
commits profile.json, comments on the Issue, closes it
```

Key things a future change needs to respect:

- **`profile.json` is the single source of personalization state** (`child`, one-time `assessment`, and the mutable `state` + `history`). The generation prompt reads it every run; only `update_profile_from_feedback.py` and `mark_word_known.py` (via their respective workflows) are supposed to write to it. `assessment.known_extra_words` is the one exception to "assessment is one-time": it's a living, parent-curated list of words confirmed known regardless of what the CEFR list or the model's own judgment would say, and the prompt must treat it as highest-priority — skip listing those words no matter what.
- **`prompts/daily_reading.md` is a strict content contract, not a loose prompt.** It only writes `day-YYYY-MM-DD.json` and explicitly must not touch `profile.json`, `README.md`, `index.html`, `publish.sh`, `generate_html.py`, or `enrich_content.py`, and must not run `enrich_content.py`/`generate_html.py` itself — those are separate, later workflow steps. If you change the pipeline order, this file's "禁止事项" section needs to stay in sync.
- **Vocabulary selection has a specific, non-obvious rule** (documented at length in the prompt): coverage of every word the child might not know matters more than staying under `vocab_count_target` — that count is a soft cap, not a quota to fill or a hard ceiling to enforce. "Might not know" is now checked primarily against `data/cefrj-vocabulary-profile.csv` (the CEFR-J word list, ~8k headwords tagged A1/A2/B1/B2) using the known-word band spelled out in `profile.json`'s `state.difficulty_scale`; the old "would a ~7-8 year old native speaker know this" heuristic is kept only as a fallback for words absent from that list (proper nouns, slang, compounds, etc.). `validate_reading.py` cross-checks the same list and prints non-blocking `WARN:` lines for likely-uncovered words — it never fails the run over this.
- **`enrich_content.py` is failure-tolerant by design**: a failed TTS or IPA lookup for one word only skips that word/audio and logs a warning, it never aborts the run (the page falls back to browser TTS if `story.mp3` is missing).
- **The daily trigger is currently manual-only** (`workflow_dispatch`), unlike the sibling `daily-ai-news` project which uses an external cron-job.org call — this project hasn't had a schedule wired up yet ("内容方向还在持续调整中" per README).
- **`publish.sh`** follows the same archive/latest/index pattern as `daily-ai-news`'s `publish.sh`: dated files move into `archive/YYYY-MM/`, `latest.*` always point at the most recent publish, and `index.html` is regenerated from scratch each run rather than hand-edited.

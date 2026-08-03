# data/

Reference data for the daily generation pipeline. Read-only — nothing in this
repo writes to files here.

## cefrj-vocabulary-profile.csv

Source: [openlanguageprofiles/olp-en-cefrj](https://github.com/openlanguageprofiles/olp-en-cefrj),
`cefrj-vocabulary-profile-1.5.csv`, fetched 2026-08-03.

CEFR-J Vocabulary Profile, © Tono Laboratory, Tokyo University of Foreign
Studies. Free for research and commercial use, provided the dataset is
cited properly (see the source repo for the full citation).

Columns: `headword,pos,CEFR,CoreInventory 1,CoreInventory 2,Threshold`. Only
`headword`, `pos`, and `CEFR` (A1/A2/B1/B2) are used in this project.

Used as the objective "does this child already know this word" reference:

- `prompts/daily_reading.md` reads it when deciding which words go in the
  day's 生词表 (vocabulary list), matched against the CEFR band mapping in
  `profile.json`'s `state.difficulty_scale`.
- `validate_reading.py` cross-checks the generated story against it and
  prints non-blocking warnings for likely-uncovered words.

No lemmatization is applied anywhere — only exact headword matches count, so
inflected forms (plurals, past tense, etc.) that aren't already a separate
headword entry will not be recognized either way.

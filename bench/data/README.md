# Frozen benchmark datasets

| Version | File | Questions | Grades | Source worksheet |
|---|---|---:|---|---|
| v1 (default) | `ykt_primary_v1.jsonl` | 60 | 1–4 | `bench/data/sources/clean_60_primary_school.xlsx`, `clean` |
| v0 (proof of concept) | `ykt_sample.jsonl` | 61 | 1–4, 10–11 | `bench/data/sources/sample.xlsx`, first sheet |

Source paths are relative to the repository root. JSONL is UTF-8 with literal Sakha
characters and Unicode sound tokens. Each line is one exercise. The solver sees
only `instruction` and `content`; `answer` is provided only to the judge.

The benchmark is self-contained under `bench/`. The two source workbooks needed
to reproduce v0 and v1 live in `sources/`; the unused root corpus was removed.
Frozen v1 provenance retains the original `data/` source identifiers so that
moving the workbooks does not change the dataset hash or invalidate saved runs.
Put new input workbooks, including `vals_90`, in `bench/data/sources/`.

## Rebuild

```bash
python3 bench/build_dataset.py
python3 bench/build_dataset.py --version v0
```

The v1 builder reads the named `clean` sheet, excluding `wip`. It requires 60 unique
IDs, grades 1–4, nonempty instructions and answers, and no external picture flags.
The source has only ID, grade, instruction, content, and answer columns. Optional
textbook metadata absent from the sheet is left empty; it is not borrowed from v0.
The curated text includes all necessary visual clues as text or Unicode tokens.

Only surrounding whitespace, line endings, trailing spaces, grades, and blank IDs
are normalized. No answer corrections or legacy content overrides are applied to v1.
The companion `ykt_primary_v1.manifest.json` records SHA-256 hashes and counts.
Each v1 item also records its source file, worksheet, and actual spreadsheet row.

| Blank-ID sheet row | Generated ID |
|---:|---|
| 12 | `g2p1-L14-006b` |
| 13 | `g2p1-L14-006c` |
| 14 | `g2p1-L14-006d` |
| 50 | `g3p1-L33-011b` |

Suffixes follow the preceding explicit ID and identify separate benchmark items;
they do not assert a printed textbook exercise number. Row 50 is a question about
interrogative pronouns, separate from the preceding charade.

## Changes from v0

v1 retains 47 IDs, adds 13, and removes 14. All 13 v0 picture-flagged items are absent,
along with the hidden-word exercise `g3p1-L14-008`. Of the retained IDs, four have
changed question or answer text after whitespace normalization:

- `g3p1-L34-001`: replaces the mismatched instruction with six riddles and supplies
  their Unicode sound-token clues.
- `g3p1-L36-011`: adds word-pattern clues to the five `бас` questions.
- `g2p2-L33-005`: corrects and extends the gap-filling passage and its answer key.
- `g3p1-L34-011`: changes dash characters in the word-arithmetic expression.

Keep v0 and v1 scores separate. The runner defaults to `bench/results/v1/` and
rejects cached results whose recorded dataset hash differs. The original v0 run
remains in `bench/results/main/`, and its leaderboard is in the root README.

## Review note

`g2p2-L35-011` is retained exactly as supplied after whitespace normalization. Its
instruction asks for consonant-letter analysis, but its reference answer lists
four riddle solutions. The v0 judge marked consonant-analysis answers wrong against
this key. This is a known alignment concern for review before interpreting v1 scores.

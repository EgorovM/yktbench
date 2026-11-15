# Yakut bench

This benchmark evaluates models' capability speak and reason in Yakut. The public benchmark questions are created from text-only test questions given in the primary school textbooks (grades 1-4).

## Valkyrie submission

The [Valkyrie adapter](valkyrie/README.md) exports Harbor-format tasks and a
text-only model agent, with commands for publishing and running the dataset.
Exercise-specific `eval_instruction` text is shown only to the judge. Model
instructions, source data, and task files are versioned and hashed separately.

New evaluations use [`models_vals.toml`](models_vals.toml): a 15-minute answer
deadline and a 33,000-token requested output limit. Gemma 4 31B is limited by
its API to 16,384 output tokens. The historical results below retain their
original budgets.

## Current evaluation: vals_90

The [90-question dataset](data/vals_90.jsonl) comes from the `vals sub` sheet of
[`vals_90.xlsx`](data/sources/vals_90.xlsx). All 15 model runs have been launched
on Valkyrie and Modal; results are in progress. [Run IDs and monitoring commands](valkyrie/RUNS.md)
are available for the team.

Each solver receives the exercise instruction and material. The judge receives
the answer key and any exercise-specific `eval_instruction`; those instructions
are never shown to the solver. The five supplied grading instructions override
the generic rubric where specified, including accepted Russian spellings.

All 90 supplied questions are retained. Twelve rows still carry picture flags
from the source workbook; models receive text only. Two new items have no grade
metadata, and six missing IDs were generated deterministically. These details
are recorded in the [dataset manifest](data/vals_90.manifest.json).

Current vals_90 scores and the completed historical runs are reported separately.

## Results

See the **[leaderboard](LEADERBOARD.md)** for current vals_90 results by model
and school grade, token usage, run status, and the historical v1/v0 tables.
Partial runs are labelled and include their graded question counts.

The completed v1 baseline used 60 questions. Claude Fable 5.2 scored 65.0%,
Gemini 4 Argon 60.0%, and GPT-6 Astra and GPT-6.1 Sol each scored 45.0%.

![Completed v1 accuracy and partial-credit results](figures/v1_leaderboard.svg)

[How to run](USAGE.md) · [Valkyrie submission](valkyrie/README.md)

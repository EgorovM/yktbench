# SakhaBench: Sakha (Yakut) Language Primary School Knowledge Benchmark

This benchmark evaluates how well language models understand, write, and reason in Sakha (Yakut). Questions are drawn from text-only exercises in Sakha primary school textbooks (grades 1-4).

## Valkyrie submission

The [Valkyrie adapter](valkyrie/README.md) exports Harbor-format tasks and a
text-only model agent, with commands for publishing and running the dataset.
Exercise-specific `eval_instruction` text is shown only to the judge. Model
instructions, source data, and task files are versioned and hashed separately.

New evaluations use [`models_vals_modal.toml`](models_vals_modal.toml): a 15-minute answer
deadline and a 33,000-token requested output limit. Gemma 4 31B is limited by
its API to 16,384 output tokens.

## Public test dataset

The [90-question dataset](data/vals_90.jsonl) comes from the `vals sub` sheet of
[`vals_90.xlsx`](data/vals_90.xlsx). The current leaderboard covers 20 models evaluated
on Valkyrie and Modal, with all 90 questions graded for each model. [Run IDs and monitoring commands](valkyrie/RUNS.md)
are available for the team.

Each solver receives the exercise instruction and material. The judge receives
the answer key and any exercise-specific `eval_instruction`; those instructions
are never shown to the solver. The five supplied grading instructions override
the generic rubric where specified, including accepted Russian spellings.

All 90 supplied questions are retained. Twelve rows still carry picture flags
from the source workbook; models receive text only. Two new items have no grade
metadata, and six missing IDs were generated deterministically. These details
are recorded in the [dataset manifest](data/vals_90.manifest.json).

## Results

See **[Leaderboard](LEADERBOARD.md)** for accuracy by model and school grade,
partial credit, token usage, and an extended cost and latency table. Scores are
sorted by All accuracy. All 20 models have completed the 90-question evaluation.

[How to run](USAGE.md) · [Valkyrie submission](valkyrie/README.md)

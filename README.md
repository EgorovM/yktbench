# ykt_bench

Sakha (Yakut) language textbook assignments and an LLM eval built from them.

- `data/` — assignments parsed from the textbooks (see `data/README.md`)
- `bench/` — eval: ask frontier models the questions, grade with an LLM judge (see `bench/README.md`)

## Current benchmark: v1

**v1 supersedes v0 as the current benchmark.** The v1 leaderboard is pending;
the v0 results below are retained for historical reference.

The default benchmark now uses the 60 exercises on the `clean` sheet of
[`clean_60_primary_school.xlsx`](data/clean_60_primary_school.xlsx): grade 1 (10),
grade 2 (20), grade 3 (25), and grade 4 (5). Required clues are supplied as text,
including Unicode sound tokens; no external pictures are needed.

The frozen UTF-8 dataset is [`bench/data/ykt_primary_v1.jsonl`](bench/data/ykt_primary_v1.jsonl).
Rebuild it with `python3 bench/build_dataset.py`; run it with `bash bench/run.sh`.
New results go to `bench/results/v1/`, with a separate smoke run in
`bench/results/v1-smoke/`. v1 evaluation is in progress; the table below records v0.

## v0 — proof of concept

Results from the original 61-question sample (grades 1–4 and 10–11), with one
answer per model and question. Judge: GPT 6.1 Sol (`gpt-6.1-sol`), high reasoning
effort. Accuracy requires every reference part to be correct; partial credit is
the mean share of parts correct. Confidence intervals are 95% bootstrap intervals
over questions. Missing, refused, and truncated answers count as wrong.

| Model | Model ID | Accuracy % | 95% CI | Partial % | Avg output tokens | Avg latency (s) |
|---|---|---:|---|---:|---:|---:|
| fable-5.2 | claude-fable-5-2 | 49.2 | 36.1–62.3 | 63.0 | 772 | 9 |
| gemini-4-argon | google/gemini-4-argon | 45.9 | 32.8–59.0 | 61.5 | 3769 | 67 |
| astra | gpt-6-astra | 34.4 | 23.0–45.9 | 49.8 | 1516 | 43 |
| grok-4.7 | x-ai/grok-4.7 | 26.2 | 14.8–37.7 | 40.7 | 27180 | 535 |
| inkling-flagship | thinkingmachines/inkling | 26.2 | 16.4–37.7 | 40.5 | 8154 | 92 |
| deepseek-v4 | deepseek/deepseek-v4-pro | 23.0 | 13.1–34.4 | 35.4 | 7061 | 93 |
| deepseek-v4.1-flash | deepseek/deepseek-v4.1-flash | 23.0 | 13.1–34.4 | 39.0 | 10322 | 53 |
| inkling-2-small | thinkingmachines/inkling-2-small | 19.7 | 9.8–31.1 | 33.0 | 11282 | 60 |
| glm-5.3 | z-ai/glm-5.3 | 16.4 | 6.6–26.2 | 20.9 | 17072 | 129 |
| gemma-4-31b | google/gemma-4-31b-it | 8.2 | 1.6–14.8 | 10.1 | 1756 | 14 |

This initial sample includes 13 picture-flagged questions, although solvers
received text only, and some prompt/answer-key alignment issues. These scores
are a proof of concept; later dataset versions should be evaluated separately.
Reasoning settings and effective token budgets differ across providers; Grok
reported output usage above its requested limit. See [benchmark documentation](bench/README.md)
for model settings and grading rules.

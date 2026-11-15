# ykt_bench

Sakha (Yakut) language textbook assignments and an LLM eval built from them.

- `data/` — assignments parsed from the textbooks (see `data/README.md`)
- `bench/` — eval: ask frontier models the questions, grade with an LLM judge (see `bench/README.md`)

## Current benchmark: v1

**v1 supersedes v0 as the current benchmark.** The v0 results below are retained
for historical reference.

The benchmark uses the 60 exercises on the `clean` sheet of
[`clean_60_primary_school.xlsx`](data/clean_60_primary_school.xlsx): grade 1 (10),
grade 2 (20), grade 3 (25), and grade 4 (5). Required clues are supplied as text,
including Unicode sound tokens; no external pictures are needed.

**Preliminary leaderboard — 2026-11-15T20:30:48+00:00**. 899/900 answers graded.
Fourteen models have finished. Sol has one question pending; its provisional
percentages use 59 graded questions. Every completed row uses all 60 questions.

Accuracy requires every reference part to be correct. Partial credit is the mean
share of parts correct. Judge: GPT 6.1 Sol, high reasoning effort. Solvers received
no browsing or external tools, and the ten original v0 solver settings are unchanged.

| Model | Graded | Accuracy % | Partial % | Requested output limit | Max reported output tokens | Over-limit answers |
|---|---:|---:|---:|---:|---:|---:|
| fable-5.2 | 60/60 | 65.0 | 81.2 | 32,000 | 13,940 | 0 |
| gemini-4-argon | 60/60 | 60.0 | 72.1 | 32,000 | 32,000 | 0 |
| sol-6.1-eval **(judge model)** † | 59/60 | 45.8 | 66.2 | 32,000 | 9,657 | 0 |
| astra | 60/60 | 45.0 | 62.7 | 32,000 | 11,750 | 0 |
| grok-4.7 | 60/60 | 36.7 | 55.4 | 32,000 | 99,878 | 36 |
| deepseek-v4.1-flash | 60/60 | 31.7 | 46.9 | 32,000 | 32,000 | 0 |
| deepseek-v4 | 60/60 | 28.3 | 47.5 | 32,000 | 32,000 | 0 |
| qwen-3.8-max | 60/60 | 25.0 | 43.3 | 32,000 | 32,000 | 0 |
| inkling-flagship | 60/60 | 21.7 | 43.9 | 32,000 | 32,000 | 0 |
| inkling-2-small | 60/60 | 21.7 | 33.7 | 32,000 | 32,000 | 0 |
| qwen-3.8-flash | 60/60 | 13.3 | 15.3 | 32,000 | 32,000 | 0 |
| glm-5.3 | 60/60 | 10.0 | 18.3 | 32,000 | 32,000 | 0 |
| qwen-3.8-27b | 60/60 | 8.3 | 11.8 | 32,000 | 27,411 | 0 |
| gigachat-3.5 | 60/60 | 6.7 | 21.5 | 32,000 | 596 | 0 |
| gemma-4-31b | 60/60 | 6.7 | 11.2 | 16,384 | 16,384 | 0 |

† Sol is still pending and its row is provisional. It also serves as the judge,
so its answers are self-judged. Its solver budget is 32,000 tokens; the judge
retains its 16,000-token grading budget.

Max reported output usage can include reasoning tokens. Responses above their
requested output limits were retained and flagged. The table counts main-run
overages; smoke-run overages are recorded separately in local results.

Qwen3.8 Flash is the official hosted counterpart based on Flash-Next; see the
[Qwen model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next). Exact API model
identifiers and settings are in [`bench/models.toml`](bench/models.toml).

The frozen UTF-8 dataset is [`bench/data/ykt_primary_v1.jsonl`](bench/data/ykt_primary_v1.jsonl).
Rebuild it with `python3 bench/build_dataset.py`; run it with `bash bench/run.sh`.
Results go to `bench/results/v1/`, with a separate smoke run in
`bench/results/v1-smoke/`. A supplied instruction/key alignment concern remains
documented in the [dataset notes](bench/data/README.md).

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

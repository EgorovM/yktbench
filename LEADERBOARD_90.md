# Yakut Benchmark Leaderboard

## vals_90

Snapshot: 2026-11-15T21:56:07+00:00. Scores are percentages.

**Evaluation is in progress.** Partial scores use graded questions only;
their denominators differ and they are not final rankings. API failures
remain ungraded. Grade cells show accuracy followed by graded/total questions.
Bold accuracy marks the best completed run; bold token usage marks the largest observed report.

| Model Name | Company | All | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Graded | Partial credit | Max reported output tokens | Over limit | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Fable 5.2 | Anthropic | **64.4** | 90.9 (11/11) | 56.0 (25/25) | 71.4 (28/28) | 50.0 (24/24) | 90/90 | 78.7 | 14149 | 0 | Complete |
| GPT-6 Astra | OpenAI | 41.1 | 45.5 (11/11) | 44.0 (25/25) | 39.3 (28/28) | 37.5 (24/24) | 90/90 | 61.2 | 21775 | 0 | Complete |
| GPT-6.1 Sol **(judge model)** | OpenAI | 38.9 | 45.5 (11/11) | 36.0 (25/25) | 50.0 (28/28) | 25.0 (24/24) | 90/90 | 58.8 | 28446 | 0 | Complete |
| Inkling 2 Small | Thinking Machines Lab | 22.2 | 27.3 (11/11) | 16.0 (25/25) | 32.1 (28/28) | 16.7 (24/24) | 90/90 | 34.5 | 33000 | 0 | Complete |
| GLM 5.3 | Z.ai | 14.4 | 18.2 (11/11) | 12.0 (25/25) | 21.4 (28/28) | 8.3 (24/24) | 90/90 | 21.9 | 33000 | 0 | Complete |
| GigaChat 3.5 Ultra | Sber | 6.7 | 9.1 (11/11) | 12.0 (25/25) | 3.6 (28/28) | 4.2 (24/24) | 90/90 | 14.2 | 900 | 0 | Complete |
| Qwen3.8 Max | Alibaba | 100.0 | — (0/11) | 100.0 (1/25) | — (0/28) | — (0/24) | 1/90 | 100.0 | — | — | API errors |
| Inkling | Thinking Machines Lab | 42.9 | 0.0 (1/11) | 100.0 (2/25) | 33.3 (3/28) | 0.0 (1/24) | 7/90 | 68.6 | — | — | API errors |
| Grok 4.7 | SpaceX (xAI) | 42.5 | 14.3 (7/11) | 42.9 (14/25) | 61.5 (13/28) | 33.3 (6/24) | 40/90 | 56.0 | **41172** | 3 | Running |
| DeepSeek V4.1 Flash | DeepSeek | 27.5 | 55.6 (9/11) | 17.6 (17/25) | 36.8 (19/28) | 18.2 (22/24) | 69/90 | 41.9 | — | — | Running |
| DeepSeek V4 Pro | DeepSeek | 26.1 | 0.0 (1/11) | 20.0 (10/25) | 25.0 (8/28) | 66.7 (3/24) | 23/90 | 37.2 | — | — | API errors |
| Qwen3.8 Flash | Alibaba | 18.9 | 25.0 (4/11) | 30.8 (13/25) | 9.1 (11/28) | 11.1 (9/24) | 37/90 | 22.6 | — | — | API errors |
| Gemma 4 31B | Google | 4.5 | 0.0 (11/11) | 10.0 (20/25) | 4.8 (21/28) | 0.0 (13/24) | 66/90 | 6.0 | — | — | API errors |
| Qwen3.8 27B | Alibaba | 0.0 | — (0/11) | 0.0 (1/25) | 0.0 (3/28) | — (0/24) | 4/90 | 3.1 | — | — | API errors |
| Gemini 4 Argon | Google | — | — (0/11) | — (0/25) | — (0/28) | — (0/24) | 0/90 | — | — | — | API errors |

Two questions have unspecified grades; they count in All, but not in grade columns.
Twelve source rows carry picture flags; solvers receive text only. All 90 supplied rows are retained.

Solvers have no browsing or tools, a 900-second answer deadline, and a requested
33,000-token output limit (Gemma: 16,384). GPT-6.1 Sol grades with a 16,000-token
budget and receives each question's `eval_instruction`; solvers do not.
Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.
Usage for unfinished runs may cover only a subset of graded answers.
A dash means usage has not yet been collected. Over-limit answers are retained and flagged.

[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)

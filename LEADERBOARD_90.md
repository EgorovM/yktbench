# Yakut Benchmark Leaderboard

## vals_90

Snapshot: 2026-11-15T22:59:26+00:00. Scores are percentages.

**Evaluation incomplete: 9/15 models fully graded.** Partial scores use graded questions only;
their denominators differ and they are not final rankings. API failures
remain ungraded. Grade columns show accuracy percentages.
Bold accuracy marks the best completed run; bold token usage marks the largest observed report.

| Model Name | Company | All | Partial credit | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Graded | Max reported output tokens | Over limit | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Fable 5.2 | Anthropic | **64.4** | 78.7 | 90.9 | 56.0 | 71.4 | 50.0 | 90/90 | 14149 | 0 | Complete |
| GPT-6 Astra | OpenAI | 41.1 | 61.2 | 45.5 | 44.0 | 39.3 | 37.5 | 90/90 | 21775 | 0 | Complete |
| GPT-6.1 Sol **(judge model)** | OpenAI | 38.9 | 58.8 | 45.5 | 36.0 | 50.0 | 25.0 | 90/90 | 28446 | 0 | Complete |
| DeepSeek V4.1 Flash | DeepSeek | 25.6 | 42.3 | 45.5 | 20.0 | 32.1 | 16.7 | 90/90 | 33000 | 0 | Complete |
| Grok 4.7 | SpaceX (xAI) | 23.3 | 32.3 | 18.2 | 32.0 | 28.6 | 12.5 | 90/90 | **51390** | 26 | Complete |
| Inkling 2 Small | Thinking Machines Lab | 22.2 | 34.5 | 27.3 | 16.0 | 32.1 | 16.7 | 90/90 | 33000 | 0 | Complete |
| GLM 5.3 | Z.ai | 14.4 | 21.9 | 18.2 | 12.0 | 21.4 | 8.3 | 90/90 | 33000 | 0 | Complete |
| Qwen3.8 27B | Alibaba | 6.7 | 9.3 | 9.1 | 0.0 | 10.7 | 8.3 | 90/90 | 33000 | 0 | Complete |
| GigaChat 3.5 Ultra | Sber | 6.7 | 14.2 | 9.1 | 12.0 | 3.6 | 4.2 | 90/90 | 900 | 0 | Complete |
| Qwen3.8 Max | Alibaba | 100.0 | 100.0 | — | 100.0 | — | — | 1/90 | — | — | API errors |
| Inkling | Thinking Machines Lab | 42.9 | 68.6 | 0.0 | 100.0 | 33.3 | 0.0 | 7/90 | — | — | API errors |
| DeepSeek V4 Pro | DeepSeek | 26.1 | 37.2 | 0.0 | 20.0 | 25.0 | 66.7 | 23/90 | — | — | API errors |
| Qwen3.8 Flash | Alibaba | 18.9 | 22.6 | 25.0 | 30.8 | 9.1 | 11.1 | 37/90 | — | — | API errors |
| Gemma 4 31B | Google | 4.5 | 6.0 | 0.0 | 10.0 | 4.8 | 0.0 | 66/90 | — | — | API errors |
| Gemini 4 Argon | Google | — | — | — | — | — | — | 0/90 | — | — | API errors |

Two questions have unspecified grades; they count in All, but not in grade columns.
Twelve source rows carry picture flags; solvers receive text only. All 90 supplied rows are retained.

Solvers have no browsing or tools, a 900-second answer deadline, and a requested
33,000-token output limit (Gemma: 16,384). GPT-6.1 Sol grades with a 16,000-token
budget and receives each question's `eval_instruction`; solvers do not.
Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.
Usage for unfinished runs may cover only a subset of graded answers.
A dash means usage has not yet been collected. Over-limit answers are retained and flagged.

[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)

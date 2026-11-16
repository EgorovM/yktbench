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

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T02:22:54+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.
Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.
Pricing snapshot: 2026-11-16T02:22:54+00:00. Input and output prices are USD per 1M tokens.

| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 90/90 | 16.7 | 8.4 | 48.7 | 195.6 | 0 | 38,014 | 111,826 | 90/90 | 8 | 40 | 4.7772* | — | 0/90 |
| GPT-6 Astra | OpenAI | 90/90 | 63.7 | 31.0 | 235.4 | 563.7 | 0 | 27,768 | 215,344 | 90/90 | 10 | 50 | 11.0449* | — | 0/90 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 90/90 | 56.5 | 23.8 | 179.6 | 608.1 | 0 | 27,768 | 210,598 | 90/90 | 2 | 10 | 2.1615* | — | 0/90 |
| DeepSeek V4.1 Flash | DeepSeek | 90/90 | 66.2 | 46.7 | 186.6 | 253.3 | 0 | 31,010 | 1,096,750 | 90/90 | 0.14 | 0.42 | 0.4650* | 0.0866 | 9/90 |
| Grok 4.7 | SpaceX (xAI) | 90/90 | 601.3 | 696.2 | 900.0 | 900.0 | 29 | 93,698† | 1,578,639† | 61/90 | 2 | 6 | 9.6592*† | 9.5342 | 61/90 |
| Inkling 2 Small | Thinking Machines Lab | 90/90 | 94.2 | 69.5 | 310.6 | 385.4 | 0 | 30,830 | 1,423,542 | 90/90 | 0.3 | 1 | 1.4328* | 1.3956 | 88/90 |
| GLM 5.3 | Z.ai | 90/90 | 139.0 | 80.3 | 428.1 | 534.2 | 0 | 29,788 | 1,422,380 | 90/90 | 0.0699 | 1.4 | 1.9934* | 4.2059 | 90/90 |
| Qwen3.8 27B | Alibaba | 90/90 | 234.5 | 254.8 | 322.4 | 900.0 | 3 | 32,625† | 2,015,027† | 87/90 | 0.15 | 1.875 | 3.7831*† | 0.0941 | 4/90 |
| GigaChat 3.5 Ultra | Sber | 90/90 | 3.5 | 2.8 | 9.9 | 19.0 | 0 | 33,650 | 8,263 | 90/90 | 1.07 | 3.21 | 0.0625* | — | 0/90 |
| Qwen3.8 Max | Alibaba | 1/90 | 153.7 | 153.7 | 153.7 | 153.7 | 0 | 305† | 6,082† | 1/90 | 2 | 6 | 0.0371*† | 0.0371 | 1/90 |
| Inkling | Thinking Machines Lab | 7/90 | 73.8 | 37.1 | 222.8 | 222.8 | 0 | 2,115† | 72,655† | 7/90 | 1 | 4.05 | 0.2964*† | 0.2960 | 7/90 |
| DeepSeek V4 Pro | DeepSeek | 23/90 | 135.2 | 50.6 | 516.9 | 524.1 | 0 | 6,992† | 205,908† | 23/90 | 0.9 | 1.5 | 0.3152*† | 0.1033 | 23/90 |
| Qwen3.8 Flash | Alibaba | 37/90 | 374.2 | 440.4 | 497.0 | 503.3 | 0 | 13,861† | 1,002,666† | 37/90 | 0.15 | 0.47 | 0.4733*† | 0.4729 | 37/90 |
| Gemma 4 31B | Google | 66/90 | 13.9 | 5.6 | 46.8 | 192.8 | 0 | 22,171† | 95,023† | 66/90 | 0.2 | 0.4 | 0.0424*† | 0.0366 | 66/90 |
| Gemini 4 Argon | Google | 0/90 | — | — | — | — | 0 | — | — | 0/90 | 2 | 10 | — | — | 0/90 |

\* Estimated cost = (reported input tokens × input price + reported output tokens × output price) / 1,000,000.
Estimates use the current OpenRouter catalog's standard base rates; GigaChat uses user-supplied rates of $1.07 input and $3.21 output per 1M tokens.
These are API-equivalent estimates for logged usage, not historical bills or Modal GPU costs. Missing usage is not extrapolated to the full dataset.
Caching, batch discounts, time-of-day offers, and context-tier adjustments are not applied; recorded charges can differ.
Known API cost is the sum of retrieved OpenRouter charges for the selected answers, not total benchmark spend.
A dash means unavailable, not free. Cost coverage counts answers with a retrieved charge; duplicate request IDs are charged once.
Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.
Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.
[Metric and pricing snapshot](data/leaderboard_metrics.json) · [Current OpenRouter pricing catalog](https://openrouter.ai/api/v1/models) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)

<!-- COST_LATENCY_END -->


Two questions have unspecified grades; they count in All, but not in grade columns.
Twelve source rows carry picture flags; solvers receive text only. All 90 supplied rows are retained.

Solvers have no browsing or tools, a 900-second answer deadline, and a requested
33,000-token output limit (Gemma: 16,384). GPT-6.1 Sol grades with a 16,000-token
budget and receives each question's `eval_instruction`; solvers do not.
Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.
Usage for unfinished runs may cover only a subset of graded answers.
A dash means usage has not yet been collected. Over-limit answers are retained and flagged.

[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)

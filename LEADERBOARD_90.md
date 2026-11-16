# Yakut Benchmark Leaderboard

## vals_90

Snapshot: 2026-11-16T05:10:03+00:00. Scores are percentages.

**Evaluation is in progress.** Partial scores use graded questions only;
their denominators differ and they are not final rankings. Failed tasks
remain ungraded. Grade columns show accuracy percentages.
Bold accuracy marks the best completed run; bold token usage marks the largest observed report.

| Model Name | Company | All | Partial credit | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Graded | Max reported output tokens | Over limit | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Fable 5.2 | Anthropic | **64.4** | 78.7 | 90.9 | 56.0 | 71.4 | 50.0 | 90/90 | 14149 | 0 | Complete |
| GPT-6 Astra | OpenAI | 41.1 | 61.2 | 45.5 | 44.0 | 39.3 | 37.5 | 90/90 | 21775 | 0 | Complete |
| Claude Opus 5.5 | Anthropic | 41.1 | 63.2 | 27.3 | 40.0 | 42.9 | 45.8 | 90/90 | 15301 | 0 | Complete |
| GPT-6.1 Sol **(judge model)** | OpenAI | 38.9 | 58.8 | 45.5 | 36.0 | 50.0 | 25.0 | 90/90 | 28446 | 0 | Complete |
| DeepSeek V4.1 Flash | DeepSeek | 25.6 | 42.3 | 45.5 | 20.0 | 32.1 | 16.7 | 90/90 | 33000 | 0 | Complete |
| Grok 4.7 | SpaceX (xAI) | 23.3 | 32.3 | 18.2 | 32.0 | 28.6 | 12.5 | 90/90 | **51390** | 26 | Complete |
| Inkling 2 Small | Thinking Machines Lab | 22.2 | 34.5 | 27.3 | 16.0 | 32.1 | 16.7 | 90/90 | 33000 | 0 | Complete |
| Muse Spark Open | Meta | 21.1 | 41.8 | 18.2 | 24.0 | 17.9 | 25.0 | 90/90 | 33000 | 0 | Complete |
| GLM 5.3 | Z.ai | 14.4 | 21.9 | 18.2 | 12.0 | 21.4 | 8.3 | 90/90 | 33000 | 0 | Complete |
| Qwen3.8 27B | Alibaba | 6.7 | 9.3 | 9.1 | 0.0 | 10.7 | 8.3 | 90/90 | 33000 | 0 | Complete |
| GigaChat 3.5 Ultra | Sber | 6.7 | 14.2 | 9.1 | 12.0 | 3.6 | 4.2 | 90/90 | 900 | 0 | Complete |
| Gemma 4 31B | Google | 4.4 | 6.4 | 0.0 | 8.0 | 3.6 | 4.2 | 90/90 | 16384 | 0 | Complete |
| Gemini 4 Carbon | Google | 80.0 | 87.2 | 66.7 | 88.9 | — | — | 15/90 | 17820 | 0 | Running |
| Qwen3.8 2.4T A95B | Alibaba | 28.1 | 41.5 | 9.1 | 37.5 | 23.8 | 100.0 | 57/90 | 33000 | 0 | Running |
| Inkling NVFP4 | Thinking Machines Lab | 27.8 | 45.9 | 45.5 | 22.7 | 23.5 | 25.0 | 54/90 | 33000 | 0 | Running |
| DeepSeek V4 Pro | DeepSeek | 26.1 | 37.2 | 0.0 | 20.0 | 25.0 | 66.7 | 23/90 | 33000 | 0 | Run errors |
| Inkling | Thinking Machines Lab | 23.1 | 46.5 | 30.0 | 0.0 | — | — | 13/90 | 14633 | 0 | Running |
| Qwen3.8 Flash | Alibaba | 18.9 | 22.6 | 25.0 | 30.8 | 9.1 | 11.1 | 37/90 | 33000 | 0 | Run errors |
| Kimi K3.1 Pro | Moonshot AI | 12.4 | 21.2 | 9.1 | 12.0 | 10.7 | 17.4 | 89/90 | 33000 | 0 | Running |
| Mistral Large 4 | Mistral AI | 6.1 | 7.6 | 0.0 | 14.3 | 4.8 | — | 33/90 | 33000 | 0 | Running |
| MiniMax M3.1 Flash | MiniMax | 1.8 | 1.8 | 0.0 | 5.0 | 0.0 | 0.0 | 55/90 | 33000 | 0 | Running |

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T05:10:04+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.
Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.
Pricing snapshot: 2026-11-16T05:04:34+00:00. Input and output prices are USD per 1M tokens.

| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 90/90 | 16.7 | 8.4 | 48.7 | 195.6 | 0 | 38,014 | 111,826 | 90/90 | 8 | 40 | 4.7772* | 4.7772* | 0/90 |
| GPT-6 Astra | OpenAI | 90/90 | 63.7 | 31.0 | 235.4 | 563.7 | 0 | 27,768 | 215,344 | 90/90 | 10 | 50 | 11.0449* | 11.0449* | 0/90 |
| Claude Opus 5.5 | Anthropic | 90/90 | 21.4 | 13.5 | 63.5 | 182.9 | 0 | 38,014 | 140,984 | 90/90 | 4 | 20 | 2.9717* | 2.9717 | 90/90 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 90/90 | 56.5 | 23.8 | 179.6 | 608.1 | 0 | 27,768 | 210,598 | 90/90 | 2 | 10 | 2.1615* | 2.1615* | 0/90 |
| DeepSeek V4.1 Flash | DeepSeek | 90/90 | 66.2 | 46.7 | 186.6 | 253.3 | 0 | 31,010 | 1,096,750 | 90/90 | 0.14 | 0.42 | 0.4650* | 0.0866 | 9/90 |
| Grok 4.7 | SpaceX (xAI) | 90/90 | 601.3 | 696.2 | 900.0 | 900.0 | 29 | 93,698† | 1,578,639† | 61/90 | 2 | 6 | 9.6592*† | 9.5342 | 61/90 |
| Inkling 2 Small | Thinking Machines Lab | 90/90 | 94.2 | 69.5 | 310.6 | 385.4 | 0 | 30,830 | 1,423,542 | 90/90 | 0.3 | 1 | 1.4328* | 1.3956 | 88/90 |
| Muse Spark Open | Meta | 90/90 | 39.5 | 24.1 | 128.1 | 168.6 | 0 | 40,129 | 756,005 | 90/90 | 1.25 | 4.25 | 3.2632* | 3.2632* | 0/90 |
| GLM 5.3 | Z.ai | 90/90 | 139.0 | 80.3 | 428.1 | 534.2 | 0 | 29,788 | 1,422,380 | 90/90 | 0.0699 | 1.4 | 1.9934* | 4.2059 | 90/90 |
| Qwen3.8 27B | Alibaba | 90/90 | 234.5 | 254.8 | 322.4 | 900.0 | 3 | 32,625† | 2,015,027† | 87/90 | 0.15 | 1.875 | 3.7831*† | 0.0941 | 4/90 |
| GigaChat 3.5 Ultra | Sber | 90/90 | 3.5 | 2.8 | 9.9 | 19.0 | 0 | 33,650 | 8,263 | 90/90 | 1.07 | 3.21 | 0.0625* | 0.0625* | 0/90 |
| Gemma 4 31B | Google | 90/90 | 18.5 | 8.1 | 62.8 | 329.6 | 0 | 29,739 | 130,015 | 90/90 | 0.2 | 0.4 | 0.0580* | 0.0366 | 66/90 |
| Gemini 4 Carbon | Google | 15/90 | 88.6 | 61.0 | 264.0 | 264.0 | 0 | 5,001† | 90,673† | 15/90 | 2 | 10 | 0.9167*† | 0.4935 | 9/90 |
| Qwen3.8 2.4T A95B | Alibaba | 57/90 | 80.8 | 50.3 | 214.9 | 239.7 | 0 | 20,619† | 715,071† | 57/90 | 2 | 6 | 4.3317*† | 4.3317*† | 0/90 |
| Inkling NVFP4 | Thinking Machines Lab | 54/90 | 84.0 | 57.9 | 236.3 | 270.0 | 0 | 16,495† | 516,525† | 54/90 | 1 | 4.05 | 2.1084*† | 2.1084*† | 0/90 |
| DeepSeek V4 Pro | DeepSeek | 23/90 | 135.2 | 50.6 | 516.9 | 524.1 | 0 | 6,992† | 205,908† | 23/90 | 0.9 | 1.5 | 0.3152*† | 0.1033 | 23/90 |
| Inkling | Thinking Machines Lab | 13/90 | 62.3 | 41.2 | 177.2 | 177.2 | 0 | 3,951† | 81,803† | 13/90 | 1 | 4.05 | 0.3353*† | 0.2309 | 10/90 |
| Qwen3.8 Flash | Alibaba | 37/90 | 374.2 | 440.4 | 497.0 | 503.3 | 0 | 13,861† | 1,002,666† | 37/90 | 0.15 | 0.47 | 0.4733*† | 0.4729 | 37/90 |
| Kimi K3.1 Pro | Moonshot AI | 89/90 | 44.1 | 29.2 | 186.3 | 230.6 | 0 | 36,804† | 536,270† | 89/90 | 0.2403 | 8.4023 | 4.5147*† | 4.5147*† | 0/90 |
| Mistral Large 4 | Mistral AI | 33/90 | 157.9 | 152.2 | 333.0 | 333.6 | 0 | 9,514† | 572,734† | 33/90 | 0.7 | 2.1 | 1.2094*† | 0.9294 | 28/90 |
| MiniMax M3.1 Flash | MiniMax | 55/90 | 117.9 | 124.0 | 215.2 | 307.1 | 0 | 27,420† | 1,220,118† | 55/90 | 0.15 | 0.6 | 0.7362*† | 0.6694 | 51/90 |

\* Estimated cost = (reported input tokens × input price + reported output tokens × output price) / 1,000,000.
Estimates use the current OpenRouter catalog's standard base rates; GigaChat uses user-supplied rates of $1.07 input and $3.21 output per 1M tokens.
These are API-equivalent estimates for logged usage, not historical bills or Modal GPU costs. Missing usage is not extrapolated to the full dataset.
Caching, batch discounts, time-of-day offers, and context-tier adjustments are not applied; recorded charges can differ.
Inkling NVFP4 uses standard Inkling API prices for its estimate; its Modal serving variant is recorded separately.
Known API cost shows the sum of retrieved OpenRouter charges when available; otherwise it shows the token-based estimate marked with \*. It is not total benchmark spend.
A dash means no reported token usage or charge is available, not free. Cost coverage counts only answers with a retrieved charge, including when a starred estimate is displayed; duplicate request IDs are charged once.
Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.
Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.
[Metric and pricing snapshot](data/leaderboard_metrics.json) · [Current OpenRouter pricing catalog](https://openrouter.ai/api/v1/models) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)

<!-- COST_LATENCY_END -->

The expanded Modal runs use Muse Spark Open, Kimi K3.1 Pro, Qwen3.8 2.4T A95B, and Inkling NVFP4.
Qwen3.8 2.4T A95B replaces the Max-0902 row. Inkling NVFP4 and the fresh Inkling flagship evaluation have separate rows.
Gemini 4 Carbon replaces the empty Argon row. Earlier variant scores remain archived in the run records and are not merged.
[Modal run settings and IDs](valkyrie/modal_round4.json) · [Modal model configuration](models_vals_modal.toml)

Two questions have unspecified grades; they count in All, but not in grade columns.
Twelve source rows carry picture flags; solvers receive text only. All 90 supplied rows are retained.

Solvers have no browsing or tools, a 900-second answer deadline, and a requested
33,000-token output limit (Gemma: 16,384). GPT-6.1 Sol grades with a 16,000-token
budget and receives each question's `eval_instruction`; solvers do not.
Max reported output tokens is the largest downloaded usage report, including reasoning tokens where reported.
Usage for unfinished runs may cover only a subset of graded answers.
A dash means usage has not yet been collected. Over-limit answers are retained and flagged.

[Run IDs](valkyrie/RUNS.md) · [Dataset](data/vals_90.jsonl) · [Settings](models_vals.toml)

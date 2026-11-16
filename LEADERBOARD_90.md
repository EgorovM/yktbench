# Yakut Benchmark Leaderboard

## vals_90

Snapshot: 2026-11-16T04:58:30+00:00. Scores are percentages.

**Evaluation is in progress.** Partial scores use graded questions only;
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
| Inkling NVFP4 | Thinking Machines Lab | 37.0 | 49.1 | 45.5 | 31.2 | — | — | 27/90 | 19653 | 0 | Running |
| Qwen3.8 2.4T A95B | Alibaba | 27.3 | 43.1 | 9.1 | 45.5 | — | — | 22/90 | 29054 | 0 | Running |
| DeepSeek V4 Pro | DeepSeek | 26.1 | 37.2 | 0.0 | 20.0 | 25.0 | 66.7 | 23/90 | 33000 | 0 | API errors |
| Muse Spark Open | Meta | 25.0 | 43.6 | 18.2 | 24.0 | 33.3 | — | 48/90 | 30768 | 0 | Running |
| Claude Opus 5.5 | Anthropic | 20.0 | 45.0 | 20.0 | — | — | — | 5/90 | 787 | 0 | Running |
| Qwen3.8 Flash | Alibaba | 18.9 | 22.6 | 25.0 | 30.8 | 9.1 | 11.1 | 37/90 | 33000 | 0 | API errors |
| Kimi K3.1 Pro | Moonshot AI | 11.6 | 21.5 | 9.1 | 12.5 | 12.5 | — | 43/90 | 12326 | 0 | Running |
| Gemma 4 31B | Google | 4.5 | 6.0 | 0.0 | 10.0 | 4.8 | 0.0 | 66/90 | 16384 | 0 | API errors |
| Mistral Large 4 | Mistral AI | 0.0 | 0.0 | 0.0 | 0.0 | — | — | 2/90 | 1068 | 0 | Running |
| Gemini 4 Argon | Google | — | — | — | — | — | — | 0/90 | — | — | API errors |
| MiniMax M3.1 Flash | MiniMax | — | — | — | — | — | — | 0/90 | — | — | Running |

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T04:58:30+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.
Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.
Pricing snapshot: 2026-11-16T04:57:21+00:00. Input and output prices are USD per 1M tokens.

| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 90/90 | 16.7 | 8.4 | 48.7 | 195.6 | 0 | 38,014 | 111,826 | 90/90 | 8 | 40 | 4.7772* | 4.7772* | 0/90 |
| GPT-6 Astra | OpenAI | 90/90 | 63.7 | 31.0 | 235.4 | 563.7 | 0 | 27,768 | 215,344 | 90/90 | 10 | 50 | 11.0449* | 11.0449* | 0/90 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 90/90 | 56.5 | 23.8 | 179.6 | 608.1 | 0 | 27,768 | 210,598 | 90/90 | 2 | 10 | 2.1615* | 2.1615* | 0/90 |
| DeepSeek V4.1 Flash | DeepSeek | 90/90 | 66.2 | 46.7 | 186.6 | 253.3 | 0 | 31,010 | 1,096,750 | 90/90 | 0.14 | 0.42 | 0.4650* | 0.0866 | 9/90 |
| Grok 4.7 | SpaceX (xAI) | 90/90 | 601.3 | 696.2 | 900.0 | 900.0 | 29 | 93,698† | 1,578,639† | 61/90 | 2 | 6 | 9.6592*† | 9.5342 | 61/90 |
| Inkling 2 Small | Thinking Machines Lab | 90/90 | 94.2 | 69.5 | 310.6 | 385.4 | 0 | 30,830 | 1,423,542 | 90/90 | 0.3 | 1 | 1.4328* | 1.3956 | 88/90 |
| GLM 5.3 | Z.ai | 90/90 | 139.0 | 80.3 | 428.1 | 534.2 | 0 | 29,788 | 1,422,380 | 90/90 | 0.0699 | 1.4 | 1.9934* | 4.2059 | 90/90 |
| Qwen3.8 27B | Alibaba | 90/90 | 234.5 | 254.8 | 322.4 | 900.0 | 3 | 32,625† | 2,015,027† | 87/90 | 0.15 | 1.875 | 3.7831*† | 0.0941 | 4/90 |
| GigaChat 3.5 Ultra | Sber | 90/90 | 3.5 | 2.8 | 9.9 | 19.0 | 0 | 33,650 | 8,263 | 90/90 | 1.07 | 3.21 | 0.0625* | 0.0625* | 0/90 |
| Inkling NVFP4 | Thinking Machines Lab | 27/90 | 48.4 | 34.5 | 148.4 | 161.2 | 0 | 7,847† | 151,243† | 27/90 | 1 | 4.05 | 0.6204*† | 0.6204*† | 0/90 |
| Qwen3.8 2.4T A95B | Alibaba | 22/90 | 62.1 | 46.5 | 172.1 | 174.4 | 0 | 7,808† | 209,225† | 22/90 | 2 | 6 | 1.2710*† | 1.2710*† | 0/90 |
| DeepSeek V4 Pro | DeepSeek | 23/90 | 135.2 | 50.6 | 516.9 | 524.1 | 0 | 6,992† | 205,908† | 23/90 | 0.9 | 1.5 | 0.3152*† | 0.1033 | 23/90 |
| Muse Spark Open | Meta | 48/90 | 22.5 | 16.5 | 45.3 | 128.1 | 0 | 20,962† | 244,315† | 48/90 | 1.25 | 4.25 | 1.0645*† | 1.0645*† | 0/90 |
| Claude Opus 5.5 | Anthropic | 5/90 | 9.9 | 9.8 | 14.4 | 14.4 | 0 | 1,901† | 3,325† | 5/90 | 4 | 20 | 0.0741*† | 0.0741*† | 0/90 |
| Qwen3.8 Flash | Alibaba | 37/90 | 374.2 | 440.4 | 497.0 | 503.3 | 0 | 13,861† | 1,002,666† | 37/90 | 0.15 | 0.47 | 0.4733*† | 0.4729 | 37/90 |
| Kimi K3.1 Pro | Moonshot AI | 43/90 | 25.6 | 15.8 | 71.5 | 91.0 | 0 | 17,172† | 127,179† | 43/90 | 0.2403 | 8.4023 | 1.0727*† | 1.0727*† | 0/90 |
| Gemma 4 31B | Google | 66/90 | 13.9 | 5.6 | 46.8 | 192.8 | 0 | 22,171† | 95,023† | 66/90 | 0.2 | 0.4 | 0.0424*† | 0.0366 | 66/90 |
| Mistral Large 4 | Mistral AI | 2/90 | 9.1 | 9.1 | 14.1 | 14.1 | 0 | 520† | 1,407† | 2/90 | 0.7 | 2.1 | 0.0033*† | 0.0033*† | 0/90 |
| Gemini 4 Argon | Google | 0/90 | — | — | — | — | 0 | — | — | 0/90 | 2 | 10 | — | — | 0/90 |
| MiniMax M3.1 Flash | MiniMax | 0/90 | — | — | — | — | 0 | — | — | 0/90 | 0.15 | 0.6 | — | — | 0/90 |

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
Qwen3.8 2.4T A95B replaces the Max-0902 row; Inkling NVFP4 replaces the original Inkling row.
Both replacements are fresh 90-question runs. Earlier variant scores remain archived in the run records and are not merged.
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

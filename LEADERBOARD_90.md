# Yakut Benchmark Leaderboard

## vals_90

Snapshot: 2026-11-16T05:37:28+00:00. Scores are percentages.

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
| Qwen3.8 2.4T A95B | Alibaba | 24.4 | 37.4 | 9.1 | 36.0 | 25.0 | 20.8 | 90/90 | 33000 | 0 | Complete |
| Inkling NVFP4 | Thinking Machines Lab | 24.4 | 40.8 | 45.5 | 24.0 | 21.4 | 20.8 | 90/90 | 33000 | 0 | Complete |
| Grok 4.7 | SpaceX (xAI) | 23.3 | 32.3 | 18.2 | 32.0 | 28.6 | 12.5 | 90/90 | **51390** | 26 | Complete |
| Inkling 2 Small | Thinking Machines Lab | 22.2 | 34.5 | 27.3 | 16.0 | 32.1 | 16.7 | 90/90 | 33000 | 0 | Complete |
| Muse Spark Open | Meta | 21.1 | 41.8 | 18.2 | 24.0 | 17.9 | 25.0 | 90/90 | 33000 | 0 | Complete |
| GLM 5.3 | Z.ai | 14.4 | 21.9 | 18.2 | 12.0 | 21.4 | 8.3 | 90/90 | 33000 | 0 | Complete |
| Qwen3.8 Flash | Alibaba | 14.4 | 18.8 | 9.1 | 20.0 | 17.9 | 8.3 | 90/90 | 33000 | 0 | Complete |
| Kimi K3.1 Pro | Moonshot AI | 12.2 | 21.1 | 9.1 | 12.0 | 10.7 | 16.7 | 90/90 | 33000 | 0 | Complete |
| Qwen3.8 27B | Alibaba | 6.7 | 9.3 | 9.1 | 0.0 | 10.7 | 8.3 | 90/90 | 33000 | 0 | Complete |
| GigaChat 3.5 Ultra | Sber | 6.7 | 14.2 | 9.1 | 12.0 | 3.6 | 4.2 | 90/90 | 900 | 0 | Complete |
| Gemma 4 31B | Google | 4.4 | 6.4 | 0.0 | 8.0 | 3.6 | 4.2 | 90/90 | 16384 | 0 | Complete |
| Mistral Large 4 | Mistral AI | 3.3 | 3.9 | 0.0 | 8.0 | 3.6 | 0.0 | 90/90 | 33000 | 0 | Complete |
| MiniMax M3.1 Flash | MiniMax | 2.2 | 2.7 | 0.0 | 4.0 | 0.0 | 4.2 | 90/90 | 33000 | 0 | Complete |
| Gemini 4 Carbon | Google | 52.9 | 62.2 | 45.5 | 48.0 | 64.3 | 100.0 | 51/90 | 33000 | 0 | Running |
| Inkling | Thinking Machines Lab | 24.6 | 44.4 | 27.3 | 16.0 | 31.6 | 50.0 | 57/90 | 33000 | 0 | Running |

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T05:37:54+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
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
| Qwen3.8 2.4T A95B | Alibaba | 90/90 | 97.5 | 68.1 | 220.7 | 239.7 | 0 | 34,056 | 1,374,978 | 90/90 | 2 | 6 | 8.3180* | 8.3180* | 0/90 |
| Inkling NVFP4 | Thinking Machines Lab | 90/90 | 102.7 | 89.9 | 252.8 | 282.1 | 0 | 28,398 | 1,066,946 | 90/90 | 1 | 4.05 | 4.3495* | 4.3495* | 0/90 |
| Grok 4.7 | SpaceX (xAI) | 90/90 | 601.3 | 696.2 | 900.0 | 900.0 | 29 | 93,698† | 1,578,639† | 61/90 | 2 | 6 | 9.6592*† | 9.5342 | 61/90 |
| Inkling 2 Small | Thinking Machines Lab | 90/90 | 94.2 | 69.5 | 310.6 | 385.4 | 0 | 30,830 | 1,423,542 | 90/90 | 0.3 | 1 | 1.4328* | 1.3956 | 88/90 |
| Muse Spark Open | Meta | 90/90 | 39.5 | 24.1 | 128.1 | 168.6 | 0 | 40,129 | 756,005 | 90/90 | 1.25 | 4.25 | 3.2632* | 3.2632* | 0/90 |
| GLM 5.3 | Z.ai | 90/90 | 139.0 | 80.3 | 428.1 | 534.2 | 0 | 29,788 | 1,422,380 | 90/90 | 0.0699 | 1.4 | 1.9934* | 4.2059 | 90/90 |
| Qwen3.8 Flash | Alibaba | 90/90 | 290.3 | 308.5 | 480.2 | 503.3 | 0 | 34,056 | 2,298,689 | 90/90 | 0.15 | 0.47 | 1.0855* | 0.4729 | 37/90 |
| Kimi K3.1 Pro | Moonshot AI | 90/90 | 45.3 | 29.9 | 186.3 | 230.6 | 0 | 37,198 | 554,751 | 90/90 | 0.2403 | 8.4023 | 4.6701* | 4.6701* | 0/90 |
| Qwen3.8 27B | Alibaba | 90/90 | 234.5 | 254.8 | 322.4 | 900.0 | 3 | 32,625† | 2,015,027† | 87/90 | 0.15 | 1.875 | 3.7831*† | 0.0941 | 4/90 |
| GigaChat 3.5 Ultra | Sber | 90/90 | 3.5 | 2.8 | 9.9 | 19.0 | 0 | 33,650 | 8,263 | 90/90 | 1.07 | 3.21 | 0.0625* | 0.0625* | 0/90 |
| Gemma 4 31B | Google | 90/90 | 18.5 | 8.1 | 62.8 | 329.6 | 0 | 29,739 | 130,015 | 90/90 | 0.2 | 0.4 | 0.0580* | 0.0366 | 66/90 |
| Mistral Large 4 | Mistral AI | 90/90 | 207.9 | 241.1 | 334.4 | 371.0 | 0 | 26,891 | 2,086,691 | 90/90 | 0.7 | 2.1 | 4.4009* | 4.4081 | 89/90 |
| MiniMax M3.1 Flash | MiniMax | 90/90 | 127.6 | 133.8 | 268.2 | 363.2 | 0 | 46,129 | 2,066,608 | 90/90 | 0.15 | 0.6 | 1.2469* | 1.2124 | 90/90 |
| Gemini 4 Carbon | Google | 51/90 | 244.0 | 213.3 | 528.4 | 587.8 | 0 | 17,236† | 875,059† | 51/90 | 2 | 10 | 8.7851*† | 8.7162 | 47/90 |
| Inkling | Thinking Machines Lab | 57/90 | 88.0 | 67.7 | 251.1 | 272.1 | 0 | 17,547† | 557,060† | 57/90 | 1 | 4.05 | 2.2736*† | 2.1448 | 55/90 |

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

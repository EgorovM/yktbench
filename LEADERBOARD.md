# Yakut Benchmark Leaderboards

- **[Valkyrie — 90 questions](LEADERBOARD_90.md):** current vals_90 evaluation, per-grade scores, token usage, and run status.
- **[v1 — 60 questions](LEADERBOARD_60.md):** completed baseline and token usage.

## v0 — proof of concept


Results from the original 61-question sample (grades 1–4 and 10–11), with one
answer per model and question. Judge: GPT 6.1 Sol (`gpt-6.1-sol`), high reasoning
effort. Accuracy requires every reference part to be correct; partial credit is
the mean share of parts correct.  Missing, refused, and truncated answers count as wrong.

| Model Name | Company | Accuracy % | Partial % | Avg output tokens | Avg latency (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| Claude Fable 5.2 | Anthropic | **49.2** | 63.0 | 772 | 9 |
| Gemini 4 Argon | Google | 45.9 | 61.5 | 3769 | 67 |
| GPT-6 Astra | OpenAI | 34.4 | 49.8 | 1516 | 43 |
| Grok 4.7 | SpaceX (xAI) | 26.2 | 40.7 | 27180 | 535 |
| Inkling | Thinking Machines Lab | 26.2 | 40.5 | 8154 | 92 |
| DeepSeek V4 Pro | DeepSeek | 23.0 | 35.4 | 7061 | 93 |
| DeepSeek V4.1 Flash | DeepSeek | 23.0 | 39.0 | 10322 | 53 |
| Inkling 2 Small | Thinking Machines Lab | 19.7 | 33.0 | 11282 | 60 |
| GLM 5.3 | Z.ai | 16.4 | 20.9 | 17072 | 129 |
| Gemma 4 31B | Google | 8.2 | 10.1 | 1756 | 14 |

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T04:53:03+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.
Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.
Pricing snapshot: 2026-11-16T04:53:03+00:00. Input and output prices are USD per 1M tokens.

| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 61/61 | 9.5 | 7.0 | 23.2 | 39.0 | 0 | 24,990 | 47,101 | 61/61 | 8 | 40 | 2.0840* | 2.0840* | 0/61 |
| Gemini 4 Argon | Google | 61/61 | 66.9 | 24.3 | 229.0 | 686.0 | 0 | 20,789 | 229,929 | 61/61 | 2 | 10 | 2.3409* | 2.3409 | 61/61 |
| GPT-6 Astra | OpenAI | 61/61 | 42.9 | 20.9 | 145.0 | 230.5 | 0 | 18,234 | 92,489 | 61/61 | 10 | 50 | 4.8068* | 4.8068* | 0/61 |
| Grok 4.7 | SpaceX (xAI) | 61/61 | 535.2 | 462.6 | 1308.4 | 1844.0 | 0 | 93,796 | 1,657,983 | 61/61 | 2 | 6 | 10.1355* | 10.0151 | 61/61 |
| Inkling | Thinking Machines Lab | 61/61 | 92.2 | 62.0 | 272.9 | 353.7 | 0 | 18,722 | 497,406 | 61/61 | 1 | 4.05 | 2.0332* | 2.0278 | 61/61 |
| DeepSeek V4 Pro | DeepSeek | 61/61 | 92.7 | 50.2 | 408.5 | 578.8 | 0 | 18,874 | 430,719 | 61/61 | 0.9 | 1.5 | 0.6631* | 0.3279 | 61/61 |
| DeepSeek V4.1 Flash | DeepSeek | 61/61 | 53.5 | 39.0 | 153.1 | 240.8 | 0 | 20,382 | 629,619 | 61/61 | 0.14 | 0.42 | 0.2673* | 0.3662 | 61/61 |
| Inkling 2 Small | Thinking Machines Lab | 61/61 | 59.7 | 39.5 | 209.8 | 254.1 | 0 | 20,183 | 688,224 | 61/61 | 0.3 | 1 | 0.6943* | 0.6352 | 61/61 |
| GLM 5.3 | Z.ai | 61/61 | 128.8 | 78.5 | 287.5 | 400.6 | 0 | 19,614 | 1,041,369 | 61/61 | 0.0699 | 1.4 | 1.4593* | 1.8543 | 61/61 |
| Gemma 4 31B | Google | 61/61 | 14.3 | 5.2 | 81.7 | 215.2 | 0 | 19,666 | 107,087 | 61/61 | 0.2 | 0.4 | 0.0468* | 0.0458 | 61/61 |

\* Estimated cost = (reported input tokens × input price + reported output tokens × output price) / 1,000,000.
Estimates use the current OpenRouter catalog's standard base rates; GigaChat uses user-supplied rates of $1.07 input and $3.21 output per 1M tokens.
These are API-equivalent estimates for logged usage, not historical bills or Modal GPU costs. Missing usage is not extrapolated to the full dataset.
Caching, batch discounts, time-of-day offers, and context-tier adjustments are not applied; recorded charges can differ.
Known API cost shows the sum of retrieved OpenRouter charges when available; otherwise it shows the token-based estimate marked with \*. It is not total benchmark spend.
A dash means no reported token usage or charge is available, not free. Cost coverage counts only answers with a retrieved charge, including when a starred estimate is displayed; duplicate request IDs are charged once.
Judging, discarded/failed attempts, Modal token or GPU hosting charges (including warmup), storage, and net credit adjustments are excluded.
Provider changes and native reasoning translations remain documented in the run notes; latency figures are not measurements of thinking time.
[Metric and pricing snapshot](data/leaderboard_metrics.json) · [Current OpenRouter pricing catalog](https://openrouter.ai/api/v1/models) · [OpenRouter cost metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)

<!-- COST_LATENCY_END -->


This initial sample includes 13 picture-flagged questions, although solvers
received text only, and some prompt/answer-key alignment issues. These scores
are a proof of concept; later dataset versions should be evaluated separately.
Reasoning settings and effective token budgets differ across providers; Grok
reported output usage above its requested limit. See [benchmark documentation](USAGE.md)
for model settings and grading rules.

# Yakut Benchmark — v1 (60 questions)

Results from 60 questions on the `clean` sheet of
[`clean_60_primary_school.xlsx`](data/sources/clean_60_primary_school.xlsx), grades 1–4.
All 15 models answered each question once. Judge: GPT 6.1 Sol, high reasoning effort.
Solvers received no browsing or external tools. The ten original v0 model settings
were kept unchanged. Accuracy requires every reference part to be correct; partial
credit is the mean share of parts correct.

| Model Name | Company | Accuracy % | Partial % | Max reported output tokens | Over-limit answers |
| --- | --- | ---: | ---: | ---: | ---: |
| Claude Fable 5.2 | Anthropic | **65.0** | 81.2 | 13940 | 0 |
| Gemini 4 Argon | Google | 60.0 | 72.1 | 32000 | 0 |
| GPT-6 Astra | OpenAI | 45.0 | 62.7 | 11750 | 0 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 45.0 | 65.1 | 32000 | 0 |
| Grok 4.7 | SpaceX (xAI) | 36.7 | 55.4 | **99878** | 36 |
| DeepSeek V4.1 Flash | DeepSeek | 31.7 | 46.9 | 32000 | 0 |
| DeepSeek V4 Pro | DeepSeek | 28.3 | 47.5 | 32000 | 0 |
| Qwen3.8 Max | Alibaba | 25.0 | 43.3 | 32000 | 0 |
| Inkling | Thinking Machines Lab | 21.7 | 43.9 | 32000 | 0 |
| Inkling 2 Small | Thinking Machines Lab | 21.7 | 33.7 | 32000 | 0 |
| Qwen3.8 Flash | Alibaba | 13.3 | 15.3 | 32000 | 0 |
| GLM 5.3 | Z.ai | 10.0 | 18.3 | 32000 | 0 |
| Qwen3.8 27B | Alibaba | 8.3 | 11.8 | 27411 | 0 |
| Gemma 4 31B | Google | 6.7 | 11.2 | 16384 | 0 |
| GigaChat 3.5 Ultra | Sber | 6.7 | 21.5 | 596 | 0 |

<!-- COST_LATENCY_START -->

### Cost and latency

Metrics snapshot: 2026-11-16T02:22:54+00:00. Latencies are seconds per final selected response; p95 uses nearest rank.
Timeouts are included. Latency excludes grading and sandbox setup; it can include client startup and transport.
Token totals contain reported usage only; † marks usage or estimates covering fewer than all questions. Coverage is out of the full question set.
Pricing snapshot: 2026-11-16T02:22:54+00:00. Input and output prices are USD per 1M tokens.

| Model Name | Company | Latency records | Avg (s) | Median (s) | p95 (s) | Max (s) | Timeouts | Input tokens | Output tokens | Usage coverage | Input $/1M | Output $/1M | Estimated cost (USD) | Known API cost (USD) | Cost coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Fable 5.2 | Anthropic | 60/60 | 15.6 | 7.3 | 33.5 | 173.3 | 0 | 25,038 | 74,507 | 60/60 | 8 | 40 | 3.1806* | 3.1806* | 0/60 |
| Gemini 4 Argon | Google | 60/60 | 58.0 | 20.3 | 317.9 | 543.4 | 0 | 20,758 | 223,681 | 60/60 | 2 | 10 | 2.2783* | 2.2783 | 60/60 |
| GPT-6 Astra | OpenAI | 60/60 | 90.7 | 26.6 | 180.8 | 1247.2 | 0 | 18,254 | 122,186 | 60/60 | 10 | 50 | 6.2918* | 6.2918* | 0/60 |
| GPT-6.1 Sol **(judge model)** | OpenAI | 60/60 | 49.9 | 20.3 | 146.7 | 597.9 | 0 | 18,254 | 136,065 | 60/60 | 2 | 10 | 1.3972* | 1.3972* | 0/60 |
| Grok 4.7 | SpaceX (xAI) | 60/60 | 720.9 | 763.2 | 1293.4 | 2034.8 | 0 | 92,555 | 2,339,249 | 60/60 | 2 | 6 | 14.2206* | 14.1087 | 60/60 |
| DeepSeek V4.1 Flash | DeepSeek | 60/60 | 69.0 | 47.6 | 219.4 | 290.4 | 0 | 20,391 | 753,350 | 60/60 | 0.14 | 0.42 | 0.3193* | 0.4516 | 60/60 |
| DeepSeek V4 Pro | DeepSeek | 60/60 | 111.7 | 63.8 | 462.6 | 528.7 | 0 | 18,989 | 580,190 | 60/60 | 0.9 | 1.5 | 0.8874* | 0.6149 | 60/60 |
| Qwen3.8 Max | Alibaba | 60/60 | 322.7 | 281.4 | 761.1 | 841.4 | 0 | 22,393 | 837,512 | 60/60 | 2 | 6 | 5.0699* | 5.0699 | 60/60 |
| Inkling | Thinking Machines Lab | 60/60 | 154.9 | 116.3 | 412.7 | 552.6 | 0 | 18,734 | 717,969 | 60/60 | 1 | 4.05 | 2.9265* | 2.9208 | 60/60 |
| Inkling 2 Small | Thinking Machines Lab | 60/60 | 108.9 | 69.1 | 265.6 | 308.7 | 0 | 20,268 | 981,600 | 60/60 | 0.3 | 1 | 0.9877* | 0.9332 | 60/60 |
| Qwen3.8 Flash | Alibaba | 60/60 | 365.1 | 430.0 | 573.5 | 665.6 | 0 | 22,393 | 1,512,597 | 60/60 | 0.15 | 0.47 | 0.7143* | 0.7135 | 60/60 |
| GLM 5.3 | Z.ai | 60/60 | 130.3 | 141.9 | 278.9 | 317.2 | 0 | 19,569 | 1,125,047 | 60/60 | 0.0699 | 1.4 | 1.5764* | 2.0704 | 60/60 |
| Qwen3.8 27B | Alibaba | 60/60 | 36.3 | 18.7 | 129.9 | 178.6 | 0 | 20,113 | 353,543 | 60/60 | 0.15 | 1.875 | 0.6659* | 0.7695 | 60/60 |
| Gemma 4 31B | Google | 60/60 | 15.3 | 7.9 | 47.1 | 142.7 | 0 | 19,653 | 93,707 | 60/60 | 0.2 | 0.4 | 0.0414* | 0.0380 | 60/60 |
| GigaChat 3.5 Ultra | Sber | 60/60 | 2.7 | 2.2 | 6.5 | 14.2 | 0 | 22,171 | 5,520 | 60/60 | 1.07 | 3.21 | 0.0414* | 0.0414* | 0/60 |

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


Exact API identifiers and generation settings are recorded in [`models.toml`](models.toml).

GPT 6.1 Sol is marked **(judge model)** because it also grades the benchmark.
Its solver answers receive the same 32,000-token requested budget as other main
solvers, while grading retains its 16,000-token budget. Its row is self-judged.

Qwen3.8 Flash is the official hosted model based on Flash-Next, not a claim to run
the exact downloadable Flash-Next weights. See the
[Qwen model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next).

Responses above their requested token limits were retained and flagged. API-reported
output usage can include reasoning tokens. The table counts main-run overages;
smoke-run overages are recorded separately in local results.

The UTF-8 dataset is [`data/ykt_primary_v1.jsonl`](data/ykt_primary_v1.jsonl).
Rebuild with `python3 build_dataset.py`; run with `bash run.sh`.
Detailed local results are in `results/v1/`. One supplied instruction/key
alignment concern remains documented in the [dataset notes](data/README.md).

### Example failure in v1

On five grade-4 word riddles, Grok took 33 minutes 55 seconds and reported 99,878
output tokens, against a requested limit of 32,000. It got two of the five parts
correct. The [UTF-8 question, reference answers, final response, and grading](examples/v1_grok_word_riddles.json)
show a concrete failure despite a long response. The time is API latency, not a
separate measurement of thinking time.

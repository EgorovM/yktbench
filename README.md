# Yakut bench

This benchmark evaluates models' capability speak and reason in Yakut.

The public benchmark questions are created from text-only test questions given in the primary school textbooks (grades 1-4).

## Distribution of questions

The benchmark uses the 60 exercises on the `clean` sheet of
[`clean_60_primary_school.xlsx`](data/clean_60_primary_school.xlsx): grade 1 (10),
grade 2 (20), grade 3 (25), and grade 4 (5). Required clues are supplied as text,
including Unicode sound tokens; no external pictures are needed.

Accuracy requires every reference part to be correct. Partial credit is the mean share of parts correct. 

## Model instruction
Judge: GPT 6.1 Sol, high reasoning effort.

No internet access enabled.

## Leaderboard
| Model | Graded | Accuracy % | Partial % | Requested output limit | Max output tokens (include reasoning) | Over-limit answers |
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


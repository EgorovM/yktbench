# SakhaBench: Sakha (Yakut) Language Primary School Knowledge Benchmark

This benchmark evaluates how well language models understand, write, and reason in Sakha (Yakut). Questions are drawn from text-only exercises in Sakha primary school textbooks (grades 1-4).

## Public test dataset

The [90-question dataset](data/vals_90.jsonl) comes from the `vals sub` sheet of
[`vals_90.xlsx`](data/vals_90.xlsx). The current leaderboard covers 20 models evaluated
on Valkyrie and Modal, with all 90 questions graded for each model. [Run IDs and monitoring commands](valkyrie/RUNS.md)
are available for the team.

Each solver receives the exercise instruction and material. The judge receives
the answer key and any exercise-specific `eval_instruction`; those instructions
are never shown to the solver. The five supplied grading instructions override
the generic rubric where specified, including accepted Russian spellings.

All 90 supplied questions are retained. Twelve rows still carry picture flags
from the source workbook; models receive text only. Two new items have no grade
metadata, and six missing IDs were generated deterministically. These details
are recorded in the [dataset manifest](data/vals_90.manifest.json).

## Results

See **[Leaderboard](LEADERBOARD.md)** for accuracy by model and school grade,
partial credit, token usage, and an extended cost and latency table. Scores are
sorted by All accuracy. All 20 models have completed the 90-question evaluation.

Notably, all models seem to have shallow vocabulary, fail to capture cultural code, and still make morphological mistakes in word formation. They are suprisingly good at supporting natural conversation though, until asked harder questions that show lack of depth in understanding Sakha language and culture.

### 1. Wrong reconstruction of a proverb

**Instruction:** Кистэлэҥ сурук. Буукубалары сааһылаан өс хоһоонун таһаар.

**Content:**

```
Үгсэ ыкайбаатҕын үсэб ыкайра.
```

**Reference:** Сүгэ кыайбатаҕын сүбэ кыайар.  
**Fable:** Үгэс кыайбатаҕын сүбэ кыайар.

Fable reconstructed the first word as **Үгэс** instead of **Сүгэ**.

### 2. Wrong proverb completion

For this six-part question, **none of the 20 models got all six correct**.

| Proverb | Reference answer | Models correct | Accuracy | Fable |
|---|---|---:|---:|:---:|
| 1. Кэллэрбин эрэ кэпсиэм… | Кэҕэ | **1/20** | 5% | ✗ |
| 2. Соруннарбын эрэ субурутуом… | Өрүс эстэрэ | **0/20** | 0% | ✗ |
| 3. Турдарбын халлааҥҥа тиийиэм… | Суол | **4/20** | 20% | ✓ |
| 4. Миигинэ суох ханна да олоруоххут суоҕа… | Дьиэ | **0/20** | 0% | ✗ |
| 5. Испэр киириэҥ — мэҥиэстиэм… | Сохсо | **0/20** | 0% | ✗ |
| 6. Хараҕа суоҕу харахтыам… | Үөрэх кинигэтэ | **0/20** | 0% | ✗ |

The successful models were:

- **Riddle 1:** DeepSeek V4.1 Flash.
- **Riddle 3:** Claude Fable 5.2, Claude Opus 5.5, GPT-6 Astra, and GPT-6.1 Sol.

**Five models got 1/6 correct; the other 15 got 0/6.** Overall, that is **5 correct answers out of 120 — 4.2%**.

### 3. Wrong word choice

| Question | Reference answer | Models correct | Accuracy | Fable |
|---|---|---:|---:|:---:|
| Кыһын үлэ-хамнас … | **2) үгэнэ** | 7/20 | 35% | ✓ |
| Ыраах алаастан от-мас … | **3) тиэйиллэр** | 8/20 | 40% | ✗ |
| Күн аайы муус-мас киллэриитэ, хотон бүппэт … | **4) түбүгэ** | 13/20 | 65% | ✓ |
| Кыһыҥҥы кылгас күн киирбитин … хаалыаҕыҥ. | **2) билбэккэ** | 16/20 | 80% | ✓ |

**Only two models got all four correct:** Claude Opus 5.5 and Qwen3.8 Flash.

**Fable got 3/4.** On the second question, it chose **2) тиэйэллэр** instead of **3) тиэйиллэр**.


## Valkyrie submission

The [Valkyrie adapter](valkyrie/README.md) exports Harbor-format tasks and a
text-only model agent, with commands for publishing and running the dataset.
Exercise-specific `eval_instruction` text is shown only to the judge. Model
instructions, source data, and task files are versioned and hashed separately.

New evaluations use [`models_vals_modal.toml`](models_vals_modal.toml): a 15-minute answer
deadline and a 33,000-token requested output limit. Gemma 4 31B is limited by
its API to 16,384 output tokens.


[How to run](USAGE.md) · [Valkyrie submission](valkyrie/README.md)

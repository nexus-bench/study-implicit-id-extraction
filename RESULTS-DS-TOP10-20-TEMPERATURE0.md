# DeepSeek V4.1 Flash: temperature-zero comparison

Run date: 2026-10-03. Model: `deepseek/deepseek-v4.1-flash` through OpenRouter.
This rerun pinned the same ten provider tags, in the same order, as the earlier
[temperature-one run](RESULTS-DS-TOP10-20.md). The only requested inference
setting changed was `temperature`, from 1 to 0. Each provider received the
same ten implicit `Form K111:`–`Form K120:` cases twice (20 requests). Both
runs used high reasoning effort, strict JSON schema, an 8192-token cap,
concurrency 5, and a 60-second socket timeout.

**% correct = exact expected JSON answers / 20 scheduled requests per provider.**

| Provider tag | Temperature 1 | Temperature 0 | Change | Temp 0 pass 1 | Temp 0 pass 2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| together | 70% (14/20) | 45% (9/20) | −25 pp | 5/10 | 4/10 |
| parasail/fp8 | 55% (11/20) | 60% (12/20) | +5 pp | 5/10 | 7/10 |
| baseten/fp8 | 65% (13/20) | 55% (11/20) | −10 pp | 8/10 | 3/10 |
| makora/fp8 | 45% (9/20) | 40% (8/20) | −5 pp | 5/10 | 3/10 |
| fireworks/us | 95% (19/20) | 100% (20/20) | +5 pp | 10/10 | 10/10 |
| coreweave/fp8 | 100% (20/20) | 95% (19/20) | −5 pp | 9/10 | 10/10 |
| modal | 45% (9/20) | 30% (6/20) | −15 pp | 3/10 | 3/10 |
| wafer | 20% (4/20) | 10% (2/20) | −10 pp | 1/10 | 1/10 |
| nextbit/fp8 | 95% (19/20) | 95% (19/20) | 0 pp | 9/10 | 10/10 |
| ionstream | 70% (14/20) | 55% (11/20) | −15 pp | 5/10 | 6/10 |
| **All providers** | **66% (132/200)** | **58.5% (117/200)** | **−7.5 pp** | **60/100** | **57/100** |

At temperature 0, all 200 provider/case/pass combinations were unique and all
responses reported the requested model. There were 117 correct and 83 wrong
answers, with no incomplete outputs, request errors, or retries. Every wrong
answer had an incorrect `id`; 69 used an empty `id`. OpenRouter reported a
total charge of about $0.083 for this rerun.

The [raw temperature-zero evidence](evidence/deepseek-v4.1-flash-top10-20-temperature0-2026-10-03.jsonl)
contains all requests and responses. The provider tags were fixed across runs,
but the calls happened at different times, the responses were not guaranteed
deterministic, and each pass reuses one template with ten IDs. The observed
change therefore does not isolate a causal effect of temperature. The table
shows this particular paired panel, not a general accuracy ranking.

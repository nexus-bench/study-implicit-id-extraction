# DeepSeek V4.1 Flash: top-ten, twenty-request run

Run date: 2026-10-03. Model: `deepseek/deepseek-v4.1-flash` through OpenRouter.
This run used the default settings with `--top 10`: the ten eligible provider
tags with the highest recent median throughput reported by OpenRouter. It sent
the same ten implicit `Form K111:`–`Form K120:` cases twice to each provider,
for 20 scheduled requests per provider. Each request pinned one provider tag,
disabled fallback, and requested high reasoning effort and strict JSON schema.
The run used an 8192-token cap, a 60-second socket timeout, concurrency 5, and
up to three retries after the initial attempt for HTTP 429 and 5xx.

**% correct = correct JSON answers / 20 scheduled requests per provider.**
Wrong answers and incomplete outputs count as not correct. The ten IDs are
instances of one selected template, so these percentages are a focused
diagnostic rather than estimates of general model capability.

| Provider tag | % correct | Correct | Pass 1 | Pass 2 | Wrong | Incomplete | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| together | 70% | 14/20 | 6/10 | 8/10 | 6 | 0 | 0 |
| parasail/fp8 | 55% | 11/20 | 5/10 | 6/10 | 7 | 2 | 0 |
| baseten/fp8 | 65% | 13/20 | 4/10 | 9/10 | 7 | 0 | 0 |
| makora/fp8 | 45% | 9/20 | 6/10 | 3/10 | 11 | 0 | 0 |
| fireworks/us | 95% | 19/20 | 9/10 | 10/10 | 1 | 0 | 0 |
| coreweave/fp8 | 100% | 20/20 | 10/10 | 10/10 | 0 | 0 | 0 |
| modal | 45% | 9/20 | 5/10 | 4/10 | 11 | 0 | 0 |
| wafer | 20% | 4/20 | 1/10 | 3/10 | 15 | 1 | 0 |
| nextbit/fp8 | 95% | 19/20 | 9/10 | 10/10 | 1 | 0 | 0 |
| ionstream | 70% | 14/20 | 6/10 | 8/10 | 6 | 0 | 0 |

All 200 provider/case/pass combinations are unique. Of the 200 scheduled
requests, 132 were correct, 65 were wrong, and three were incomplete. There
were no HTTP errors or retries. The three incomplete responses ended with
`finish_reason=length`: `parasail/fp8` K113 and K116 in pass 1, and `wafer`
K111 in pass 1. All 200 responses reported the requested model. OpenRouter
reported a total charge of about $0.119 for returned responses.

The [raw request/response evidence](evidence/deepseek-v4.1-flash-top10-20-2026-10-03.jsonl)
contains all 200 outcomes, including pass numbers. The provider tag identifies
OpenRouter's reported serving target, not the underlying weights or engine.
Throughput rankings can change between runs. No explicit-wording control was
run, and one case changes a provider's 20-request score by five percentage
points.

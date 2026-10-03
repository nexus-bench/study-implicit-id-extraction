# DeepSeek V4.1 Flash: top-five, twenty-request run

Run date: 2026-10-03. Model: `deepseek/deepseek-v4.1-flash` through OpenRouter.
The runner selected the five eligible provider tags with the highest recent
median throughput reported by OpenRouter. It sent the same ten implicit
`Form K111:`–`Form K120:` cases twice to each provider, for 20 scheduled
requests per provider. Each request pinned one provider tag, disabled fallback,
and requested high reasoning effort and strict JSON schema. The run used an
8192-token cap, a 60-second socket timeout, concurrency 5, and up to three
retries after the initial attempt for HTTP 429 and 5xx.

**% correct = correct JSON answers / 20 scheduled requests per provider.**
Wrong answers, incomplete outputs, and request errors count as not correct.
The ten IDs are instances of one selected template, so these percentages are
a focused diagnostic rather than estimates of general model capability.

| Provider tag | % correct | Correct | Pass 1 | Pass 2 | Wrong | Incomplete | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| together | 45% | 9/20 | 4/10 | 5/10 | 10 | 1 | 0 |
| parasail/fp8 | 45% | 9/20 | 3/10 | 6/10 | 10 | 1 | 0 |
| fireworks/us | 90% | 18/20 | 8/10 | 10/10 | 2 | 0 | 0 |
| baseten/fp8 | 55% | 11/20 | 6/10 | 5/10 | 6 | 0 | 3 |
| makora/fp8 | 55% | 11/20 | 8/10 | 3/10 | 8 | 1 | 0 |

All 100 provider/case/pass combinations are unique. Of the 100 scheduled
requests, 58 were correct, 36 were wrong, three were incomplete, and three
ended with HTTP 429 after four attempts each. The 429 errors were all on
`baseten/fp8`, which returned 17 complete answers. Its 55% score includes
rate limiting and should not be read as a 20-answer accuracy measurement.
The three incomplete responses ended with `finish_reason=length`:
`together` K118 in pass 1, `parasail/fp8` K117 in pass 2, and `makora/fp8`
K118 in pass 2. All 97 returned responses reported the requested model.
OpenRouter reported a total charge of about $0.088 for returned responses.

The [raw request/response evidence](evidence/deepseek-v4.1-flash-top5-20-2026-10-03.jsonl)
contains all 100 outcomes, including pass numbers. The provider tag identifies
OpenRouter's reported serving target, not the underlying weights or engine.
Throughput rankings can change between runs. The earlier
[ten-request top-five run](RESULTS-DS-TOP5.md) used the same model and settings
but a different live provider ordering and only one pass. No explicit-wording
control was run, and one case changes a provider's 20-request score by five
percentage points.

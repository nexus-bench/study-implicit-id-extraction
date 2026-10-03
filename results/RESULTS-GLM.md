# GLM-5.3-Flash: implicit ID extraction

Run date: 2026-10-03. Model: `z-ai/glm-5.3-flash` through OpenRouter.
This run used temperature 1.
The runner selected the five eligible provider tags with the highest recent
median throughput reported by OpenRouter, then sent the same ten
`Form K111:`–`Form K120:` cases to each. Each request pinned one provider tag,
disabled fallback, and requested high reasoning effort and strict JSON schema.
The run used an 8192-token cap, a 60-second socket timeout, concurrency 5,
and up to three retries after the initial attempt for HTTP 429 and 5xx.

**% correct = correct JSON answers / 10 scheduled requests per provider.**
Wrong answers and request errors count as not correct. The ten IDs are
instances of one selected template, so these percentages are a focused
diagnostic rather than estimates of general model capability.

| Provider tag | % correct | Correct | Wrong | Invalid / incomplete | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| friendli | 20% | 2/10 | 8 | 0 | 0 |
| baseten/fp8 | 20% | 2/10 | 3 | 0 | 5 |
| parasail/fp4 | 30% | 3/10 | 7 | 0 | 0 |
| reka | 30% | 3/10 | 7 | 0 | 0 |
| fireworks/us | 20% | 2/10 | 8 | 0 | 0 |

All 50 provider/case pairs are unique. Of the 50 scheduled requests, 12 were
correct, 33 were wrong, and five ended with HTTP 429 after four attempts each.
All five errors were on `baseten/fp8`; it returned five complete answers, of
which two were correct. Its 20% scheduled-request score therefore includes
rate limiting and should not be read as a ten-answer accuracy measurement.
The other four providers returned ten complete answers each. All 45 returned
responses reported the requested model and ended with `finish_reason=stop`.
OpenRouter reported a total charge of about $0.0024 for returned responses.

The [raw request/response evidence](evidence/glm-5.3-flash-2026-10-03.jsonl)
contains all 50 outcomes. The 429 rows record status and attempt count, but
not an HTTP response body. The provider tag identifies OpenRouter's reported
serving target, not the underlying weights or engine. Throughput rankings can
change between runs. No repeats or explicit-wording control were run, and one
case changes a provider's score by ten percentage points.

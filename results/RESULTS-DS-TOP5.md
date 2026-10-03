# DeepSeek V4.1 Flash: top-five implicit ID extraction run

Run date: 2026-10-03. Model: `deepseek/deepseek-v4.1-flash` through OpenRouter.
This run used temperature 1.
The runner selected the five eligible provider tags with the highest recent
median throughput reported by OpenRouter, then sent the same ten
`Form K111:`–`Form K120:` cases to each. Each request pinned one provider tag,
disabled fallback, and requested high reasoning effort and strict JSON schema.
The run used an 8192-token cap, a 60-second socket timeout, concurrency 5,
and up to three retries after the initial attempt for HTTP 429 and 5xx.

**% correct = correct JSON answers / 10 scheduled requests per provider.**
Wrong answers and incomplete outputs count as not correct. The ten IDs are
instances of one selected template, so these percentages are a focused
diagnostic rather than estimates of general model capability.

| Provider tag | % correct | Correct | Wrong | Invalid / incomplete | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| together | 30% | 3/10 | 6 | 1 | 0 |
| fireworks/us | 100% | 10/10 | 0 | 0 | 0 |
| parasail/fp8 | 40% | 4/10 | 6 | 0 | 0 |
| baseten/fp8 | 70% | 7/10 | 2 | 1 | 0 |
| makora/fp8 | 60% | 6/10 | 4 | 0 | 0 |

All 50 provider/case pairs are unique and completed in one attempt. Of the 50
scheduled requests, 30 were correct, 18 were wrong, and two were incomplete.
The incomplete responses were `together` on K112 and `baseten/fp8` on K111;
both ended with `finish_reason=length`. There were no request errors. Every
response reported the requested model. OpenRouter reported a total charge of
about $0.048 for the run.

The [raw request/response evidence](evidence/deepseek-v4.1-flash-top5-2026-10-03.jsonl)
contains all 50 outcomes. The provider tag identifies OpenRouter's reported
serving target, not the underlying weights or engine. Throughput rankings can
change between runs. This run used different output and concurrency settings
from the earlier [all-provider DeepSeek run](RESULTS.md), so its percentages
should not be treated as a controlled repeat. No explicit-wording control was
run, and one case changes a provider's score by ten percentage points.

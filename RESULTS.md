# DeepSeek V4.1 Flash: implicit ID extraction

Run date: 2026-10-03. Model: `deepseek/deepseek-v4.1-flash` through OpenRouter.
The runner selected 22 provider tags from the live endpoint catalog and sent
the same ten `Form K111:`–`Form K120:` cases to each. Each request pinned one
provider tag, disabled fallback, and requested high reasoning effort and strict
JSON schema. See [bench.py](bench.py) for the exact prompts and settings and
[raw request/response evidence](evidence/deepseek-v4.1-flash-2026-10-03.jsonl)
for all 220 outcomes.

**% correct = correct JSON answers / 10 scheduled requests per provider.** An
invalid or incomplete response and a request error count as not correct. The
ten IDs are instances of one selected template, so these percentages are a
focused diagnostic rather than estimates of general model capability.

| Provider tag | % correct | Correct | Wrong | Invalid / incomplete | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| atlas-cloud/fp8 | 70% | 7/10 | 3 | 0 | 0 |
| baidu/fp8 | 100% | 10/10 | 0 | 0 | 0 |
| baseten/fp8 | 50% | 5/10 | 5 | 0 | 0 |
| coreweave/fp8 | 100% | 10/10 | 0 | 0 | 0 |
| decart/fp4 | 100% | 10/10 | 0 | 0 | 0 |
| deepinfra/fp8 | 70% | 7/10 | 1 | 2 | 0 |
| dekallm | 30% | 3/10 | 6 | 1 | 0 |
| digitalocean | 20% | 2/10 | 8 | 0 | 0 |
| fireworks | 90% | 9/10 | 1 | 0 | 0 |
| fireworks/us | 100% | 10/10 | 0 | 0 | 0 |
| inference-net | 50% | 5/10 | 5 | 0 | 0 |
| ionstream | 50% | 5/10 | 5 | 0 | 0 |
| makora/fp8 | 40% | 4/10 | 6 | 0 | 0 |
| modal | 30% | 3/10 | 7 | 0 | 0 |
| morph/fp8 | 100% | 10/10 | 0 | 0 | 0 |
| nextbit/fp8 | 90% | 9/10 | 1 | 0 | 0 |
| open-inference/fp4 | 20% | 2/10 | 6 | 2 | 0 |
| parasail/fp8 | 50% | 5/10 | 5 | 0 | 0 |
| sail-research/fp4 | 90% | 9/10 | 1 | 0 | 0 |
| together | 30% | 3/10 | 7 | 0 | 0 |
| venice/fp8 | 70% | 7/10 | 2 | 1 | 0 |
| wafer | 30% | 3/10 | 7 | 0 | 0 |

All 220 provider/case pairs are unique and have one recorded attempt. Every
response reported the requested model and exactly one selected provider in
OpenRouter's routing metadata; none reported BYOK billing. There were no HTTP
or transport errors. Six responses ended with `finish_reason=length`, so they
are incomplete. All 76 wrong, complete responses had an incorrect `id`; two
also had an incorrect `nickname`. The absent `middle_name` was correct in all
76. OpenRouter's reported total charge for the run was about $0.093.

The provider tag and OpenRouter routing metadata identify the reported serving
provider, not the underlying weights, quantization, or engine. A provider tag
may represent more than one endpoint. No repeats or explicit-wording control
were run in this mirror, and one case changes a provider's score by ten
percentage points.

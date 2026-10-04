# Same requested model, different implicit-ID accuracy

On October 4, 2026 UTC, we requested `deepseek/deepseek-v4.1-flash` through every provider tag that met the study's endpoint-parameter filter. The live catalog returned 21 eligible tags. The earlier all-provider run had 22; `open-inference/fp4` was no longer eligible when this panel was frozen. This report describes the frozen 21-tag panel, not all possible serving paths.

## What we tested

We generated 100 distinct IDs (`K201`–`K300`) across five record-wording templates. Each case had two matched versions: an implied ID in a `Form K201:` heading and an explicit `Record ID: K201.` heading. The rest of the record text was identical within each pair. Every provider tag received every case in both forms at temperatures 0 and 1: 21 × 100 × 2 × 2 = 8,400 scheduled jobs. Paired jobs were adjacent in a shuffled schedule, with their order randomized.

Every request used the same system instruction, high reasoning effort, `top_p=1`, strict three-field JSON schema, 32,768 maximum output tokens, a 240-second socket timeout, a pinned provider tag, and fallback disabled. The manifest records the cases, tag list, prompt, schema, and settings. The main pass used concurrency 24. A 429 retry pass ran at concurrency 1. All 83 HTTP 429s and two 429s embedded in HTTP 200 responses resolved on retry. The archived JSONL preserves all 8,485 attempts; scoring takes the latest outcome for each job. No request errors remain in the final panel.

## What we found

**The provider spread persists on varied cases.** At temperature 0, implied-ID accuracy ranged from 46/100 to 100/100 across tags. Thirteen tags scored below 70/100; eight scored at least 96/100. At temperature 1, the range was 48/100 to 100/100. This pattern spans many tags rather than one isolated failing target. [The complete provider table](PAIRED-TABLE-20261004.md) shows all four matched scores for each tag.

**The explicit-ID control nearly closes the gap.** Across all tags, explicit-ID accuracy was 2,100/2,100 at temperature 0 and 2,099/2,100 at temperature 1. Implied-ID accuracy was 1,508/2,100 and 1,535/2,100 respectively. This supports the conclusion that the label-to-ID step is a major part of this diagnostic's difficulty. It does not identify which serving difference causes the provider spread.

**Wording matters within the implied condition.** Across 420 requests per template and temperature, implied-ID accuracy ranged from 187/420 to 389/420 at temperature 0. Explicit-ID accuracy was at least 419/420 for every template and temperature. The [template breakdown](PAIRED-TABLE-20261004.md#by-case-template) is an important limit on treating any single prompt as representative.

**Temperature did not remove the spread.** The overall implied-ID totals differed by 27 answers out of 2,100 between temperatures 0 and 1. Individual tags changed in both directions. This run was designed to compare matched settings, but one pass at each temperature is insufficient to infer a stable temperature effect.

ID accuracy is the primary metric. A valid completed JSON answer counts as ID-correct when its `id` equals the expected ID, even if another field is wrong. Exact matches across all three fields totaled 7,128/8,400. There were 42 incomplete outputs and one invalid output after retries. The report separates wrong IDs from mistakes in the other fields.

## Reproduction and limits

- [Frozen manifest](PAIRED-MANIFEST-20261004.json): provider tags, 100 cases, and request settings.
- [Full table](PAIRED-TABLE-20261004.md): provider and template results.
- [Raw request and response archive](PAIRED-RAW-20261004.jsonl.gz): all attempts, including rate limits and retries.
- Runner: `python bench.py --paired --report --manifest results/PAIRED-MANIFEST-20261004.json --output results/PAIRED-RAW-20261004.jsonl.gz`.

SHA-256: manifest `85bc77e13b47e07fa27b688387cd9625e1d7463396b9dc8ba79062e0cd888e83`; compressed raw archive `c53c38314c1bd067a967559aa0ec40baf3895fdf739ed8690aa2c5b3c560176b`.

All 8,400 final responses reported the requested model slug. OpenRouter's routing metadata reported the same selected endpoint model identifier, `deepseek/deepseek-v4.1-flash-20260910`, for all of them. Those identifiers do not verify identical weights, quantization, engines, or server-side settings. Provider tags are serving targets, and some tags share a company name. The study uses five variations of one extraction task, one panel on one date, and no direct-provider control. Its scores describe this diagnostic rather than broad model or provider quality.

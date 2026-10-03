# Implicit record ID extraction, small mirror

[DeepSeek V4.1 Flash all-provider results](RESULTS.md),
[DeepSeek top-five ten-request results](RESULTS-DS-TOP5.md),
[DeepSeek top-five twenty-request results](RESULTS-DS-TOP5-20.md),
[DeepSeek top-ten twenty-request results](RESULTS-DS-TOP10-20.md), and
[GLM-5.3-Flash top-five results](RESULTS-GLM.md) from 2026-10-03 include
provider tables and raw request/response evidence.

This standalone Python project reproduces the implicit ID extraction condition from
[`llm-provider-bench`](https://github.com/nexus-bench/llm-provider-bench). The
historical task asks a model to extract `id`, an explicitly empty `nickname`, and
an absent `middle_name`. Each provider receives the ten `Form K111:` through
`Form K120:` cases twice by default: 20 requests total. The explicit
`Record ID:` control is omitted.

The script uses OpenRouter's chat completions endpoint. Running `python bench.py`
defaults to the five fastest eligible provider tags for DeepSeek V4.1 Flash;
`--model z-ai/glm-5.3-flash` runs the same task on GLM-5.3-Flash.
Requests use `reasoning.effort=high`, strict JSON schema, temperature 1, top_p 1,
and an 8192-token cap by default. `provider.only` pins each provider tag and disables
fallbacks.

## Run

Python 3.10+ is enough; there are no runtime dependencies. Set
`OPENROUTER_API_KEY` in the environment, put an `OPENROUTER_API_KEY=...` line in
the local `.env` file, or pass `--env-file path/to/credentials.env`. An explicit
`--env-file` takes precedence over the environment; the environment takes
precedence over the local `.env`. The runner uses only that key from an env
file and never writes it to the results. The local `.env` is gitignored.

With a key available, the simplest paid run is:

```sh
python bench.py
```

Discover eligible provider tags for either model without making completion
requests:

```sh
python bench.py --model deepseek/deepseek-v4.1-flash --list-providers
python bench.py --model z-ai/glm-5.3-flash --list-providers
```

The script fetches the live [OpenRouter model endpoint catalog](https://openrouter.ai/docs/api/api-reference/endpoints/list-all-endpoints-for-a-model), keeps status-0 endpoints advertising the reasoning and structured-output parameters used here, and deduplicates provider tags. Catalog eligibility does not guarantee account access or a successful completion. A tag can represent more than one endpoint under the same provider.

To override the defaults, select a model, subset, or provider count:

```sh
python bench.py --model z-ai/glm-5.3-flash --provider deepinfra/fp4 --provider fireworks
python bench.py --model deepseek/deepseek-v4.1-flash --all-providers
python bench.py --model deepseek/deepseek-v4.1-flash --top 5
python bench.py --model z-ai/glm-5.3-flash --top 10
python bench.py --repeats 1  # ten requests per provider
python bench.py --num-requests 15 --max-tokens 4096 --concurrency 3 --timeout 90 --retries 5
```

`--top N` selects the N eligible provider tags with the highest p50 throughput
reported by OpenRouter for the last 30 minutes. Tags without a throughput
measurement are excluded, so fewer than N may be selected. Duplicate endpoints
with one tag use the highest reported throughput. This selects for speed, not
correctness, and the selected set can change between runs. `--all-providers`
makes 20 requests for every listed tag by default, so inspect the list first.
The default is five requests at once across the whole run, with a 60-second
socket timeout per attempt. `--num-requests N` sets the exact number of
scheduled requests **per provider**; the ten fuzzy cases cycle in order, so
15 means one full pass plus K111–K115 again. `--repeats N` instead sets the
number of full ten-case passes; these two flags are mutually exclusive.
`--max-tokens` changes the output cap. `--concurrency`, `--timeout`, and
`--retries` control parallel calls, socket timeout per attempt, and retries
for HTTP 429 and 5xx responses, respectively.
`Retry-After` is honored when supplied. A 429 starts a shared cooldown: all
workers wait before their next attempt, including queued requests. Requests
already in flight may finish. A 5xx backs off only its own request. Each
logical request is scored once after its final attempt.

The table leads with **% correct = correct responses / scheduled requests**
for each provider tag, and shows the count beside it (`correct/20` by default).
Wrong answers, invalid or incomplete outputs, and request errors remain
separate columns. An error or
invalid output contributes zero to `% correct`; inspect those columns before
interpreting a provider difference. While requests run, stderr shows completed
requests and outcome counts. It updates in place in a terminal and prints
occasional lines when redirected to a log. Full request and response records go to a
new timestamped `results-*.jsonl` file (gitignored) as each request finishes;
use `--output` to choose another file. Existing output files are never
overwritten. A nonzero
exit code means at least one request failed or produced an incomplete/invalid
response. This small, deliberately selected template panel is a diagnostic,
not an independent-task benchmark or a broad provider ranking. Retries can
repeat a request that the server already processed and may incur another charge.

Source: `packages/evaluation/src/id-diagnostic.ts` and
`docs/OPENROUTER_ID_STUDY.md` on the source repository's
`codex/openrouter-id-study` branch. This mirror repeats ten implicit cases
instead of its larger paired panel. The GLM model option is an extension of
the historical DeepSeek diagnostic.

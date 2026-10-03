# Implicit record ID extraction, small mirror

[DeepSeek V4.1 Flash results from 2026-10-03](RESULTS.md) include the full
provider table and raw request/response evidence.

This standalone Python project reproduces the implicit ID extraction condition from
[`llm-provider-bench`](https://github.com/nexus-bench/llm-provider-bench). The
historical task asks a model to extract `id`, an explicitly empty `nickname`, and
an absent `middle_name`. Each provider receives ten `Form K111:` through
`Form K120:` requests. The explicit `Record ID:` control is omitted.

The script uses OpenRouter's chat completions endpoint. It defaults to DeepSeek
V4.1 Flash; `--model z-ai/glm-5.3-flash` runs the same task on GLM-5.3-Flash.
Requests use `reasoning.effort=high`, strict JSON schema, temperature 1, top_p 1,
and a 4096-token cap. `provider.only` pins each provider tag and disables
fallbacks.

## Run

Python 3.10+ is enough; there are no runtime dependencies. Discover eligible
provider tags for either model without making completion requests:

```sh
python bench.py --model deepseek/deepseek-v4.1-flash --list-providers
python bench.py --model z-ai/glm-5.3-flash --list-providers
```

The script fetches the live [OpenRouter model endpoint catalog](https://openrouter.ai/docs/api/api-reference/endpoints/list-all-endpoints-for-a-model), keeps status-0 endpoints advertising the reasoning and structured-output parameters used here, and deduplicates provider tags. Catalog eligibility does not guarantee account access or a successful completion. A tag can represent more than one endpoint under the same provider.

To make paid requests, set your key and explicitly select a subset or every
eligible provider:

```sh
export OPENROUTER_API_KEY=...
python bench.py --model z-ai/glm-5.3-flash --provider deepinfra/fp4 --provider fireworks
python bench.py --model deepseek/deepseek-v4.1-flash --all-providers
```

`--all-providers` makes ten requests for every listed tag, so inspect the list
first. The default is three requests at once across the whole run. Adjust with
`--concurrency`; `--retries` controls retries for HTTP 429 and 5xx responses.
`Retry-After` is honored when supplied. Each logical request is scored once
after its final attempt.

The table leads with **% correct = correct responses / 10 scheduled requests**
for each provider tag, and shows `correct/10` beside it. Wrong answers, invalid
or incomplete outputs, and request errors remain separate columns. An error or
invalid output contributes zero to `% correct`; inspect those columns before
interpreting a provider difference. Full request and response records go to
`results.jsonl` (gitignored) as each request finishes; use `--output` to choose
another file. Existing output files are never overwritten. A nonzero
exit code means at least one request failed or produced an incomplete/invalid
response. This small, deliberately selected template panel is a diagnostic,
not an independent-task benchmark or a broad provider ranking. Retries can
repeat a request that the server already processed and may incur another charge.

Source: `packages/evaluation/src/id-diagnostic.ts` and
`docs/OPENROUTER_ID_STUDY.md` on the source repository's
`codex/openrouter-id-study` branch. This mirror uses ten implicit cases instead
of its larger paired, repeated panel. The GLM model option is an extension of
the historical DeepSeek diagnostic.

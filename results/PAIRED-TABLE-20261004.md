# Paired implicit-ID extraction: deepseek/deepseek-v4.1-flash

Final jobs: 8400/8400; raw attempts: 8485. Each score is correct ID / 100 scheduled cases. HTTP 429 and other request errors are listed separately.

| Provider tag | T0 implied | T0 explicit | T1 implied | T1 explicit | Wrong ID | Other fields wrong | Incomplete/invalid | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| atlas-cloud/fp8 | 62/100 | 100/100 | 57/100 | 100/100 | 75 | 2 | 6 | 0 |
| baidu/fp8 | 96/100 | 100/100 | 93/100 | 100/100 | 11 | 0 | 0 | 0 |
| baseten/fp8 | 59/100 | 100/100 | 60/100 | 100/100 | 74 | 0 | 7 | 0 |
| coreweave/fp8 | 100/100 | 100/100 | 97/100 | 100/100 | 3 | 6 | 0 | 0 |
| decart/fp4 | 96/100 | 100/100 | 96/100 | 100/100 | 8 | 3 | 0 | 0 |
| deepinfra/fp8 | 59/100 | 100/100 | 63/100 | 100/100 | 71 | 3 | 7 | 0 |
| dekallm | 58/100 | 100/100 | 53/100 | 100/100 | 89 | 0 | 0 | 0 |
| digitalocean | 58/100 | 100/100 | 55/100 | 100/100 | 83 | 0 | 4 | 0 |
| fireworks | 98/100 | 100/100 | 98/100 | 100/100 | 4 | 4 | 0 | 0 |
| fireworks/us | 99/100 | 100/100 | 95/100 | 100/100 | 6 | 2 | 0 | 0 |
| inference-net | 46/100 | 100/100 | 48/100 | 100/100 | 106 | 1 | 0 | 0 |
| ionstream | 59/100 | 100/100 | 68/100 | 100/100 | 67 | 0 | 6 | 0 |
| makora/fp8 | 56/100 | 100/100 | 60/100 | 100/100 | 81 | 0 | 3 | 0 |
| modal | 52/100 | 100/100 | 65/100 | 100/100 | 83 | 0 | 0 | 0 |
| morph/fp8 | 100/100 | 100/100 | 98/100 | 100/100 | 1 | 68 | 1 | 0 |
| nextbit/fp8 | 99/100 | 100/100 | 100/100 | 99/100 | 2 | 20 | 0 | 0 |
| parasail/fp8 | 50/100 | 100/100 | 58/100 | 100/100 | 90 | 0 | 2 | 0 |
| sail-research/fp4 | 99/100 | 100/100 | 95/100 | 100/100 | 6 | 5 | 0 | 0 |
| together | 50/100 | 100/100 | 58/100 | 100/100 | 88 | 0 | 4 | 0 |
| venice/fp8 | 65/100 | 100/100 | 63/100 | 100/100 | 69 | 0 | 3 | 0 |
| wafer | 47/100 | 100/100 | 55/100 | 100/100 | 98 | 0 | 0 | 0 |

Exact three-field JSON: 7128/8400 jobs.

## By case template

| Template | T0 implied | T0 explicit | T1 implied | T1 explicit |
| --- | ---: | ---: | ---: | ---: |
| 1 | 281/420 | 420/420 | 294/420 | 420/420 |
| 2 | 187/420 | 420/420 | 221/420 | 420/420 |
| 3 | 362/420 | 420/420 | 363/420 | 419/420 |
| 4 | 389/420 | 420/420 | 372/420 | 420/420 |
| 5 | 289/420 | 420/420 | 285/420 | 420/420 |

The provider tag names OpenRouter's reported serving target. It does not prove identical weights, quantization, or engines across tags.

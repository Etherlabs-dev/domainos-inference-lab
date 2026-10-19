# Experiment report · DomainOS inference lab

Experiment date: 19 October 2026. Packaging date: 19 October 2026.

## Outcome

The local Unsloth API returned a model response. Modal provisioned a remote T4, and vLLM served Qwen2.5-1.5B-Instruct through an authenticated HTTPS API. A direct Python request returned HTTP 200 and token usage. A deliberately invalid Proxy Token returned HTTP 401. The application recorded $0.18 in compute usage, and the user reported stopping it.

## Evidence basis

The code was inspected directly. Historical outcomes were recovered from the referenced “Compare AI Core Services” conversation and the user's supplied continuation summary. The conversation reader returns attachment notices, not the image files. Consequently these are conversation-reported measurements, not a new screenshot audit or a rerun. [Evidence index](../evidence/README.md) and [structured results](../evidence/results.json) retain the distinction.

| Observation | Measurement | Provenance |
| --- | --- | --- |
| Local model/API | Q4_K_M GGUF through Unsloth; response succeeded | User continuation; original `client.py` model ID and loopback route |
| Remote GPU | T4 inspection succeeded | User continuation; original `gpu_test.py` |
| Cloud model | Qwen2.5-1.5B-Instruct | Original `qwen_vllm.py` |
| Valid direct request | HTTP 200 | Lab 5 conversation summary |
| Example timing | 161.44 seconds end to end; success on attempt 24 of 30 | Lab 5 conversation summary |
| Example usage | 42 prompt, 126 completion, 168 total tokens | Lab 5 conversation summary |
| Invalid authentication | HTTP 401 | Lab 6.1 conversation summary |
| App requests | 74 total; 3 successful; 71 errors | Lab 6.2 conversation summary |
| App resource usage | T4 $0.13 + CPU $0.04 + memory $0.01 = $0.18 | Lab 6.2 conversation summary |
| Stopped app | User reported stopped | User's final experiment message |

## Measured economics

| Resource | Recorded USD | Share of rounded total |
| --- | ---: | ---: |
| T4 GPU | 0.13 | 72.22% |
| CPU | 0.04 | 22.22% |
| Memory | 0.01 | 5.56% |
| Total | **0.18** | **100%** |

Allocating the entire experiment to its three successful responses gives **$0.18 / 3 = $0.06 per successful response**. This includes startup, readiness traffic, idle/runtime overhead and testing. It is an experiment allocation, not the marginal cost of generating a response or a service price.

The 168-token observation belongs to one response. Total experiment tokens and resource-active seconds were not captured in the accessible evidence, so a cost-per-1,000-token figure cannot be calculated from this record. Dividing the full $0.18 by those 168 tokens would mix incompatible measurement windows. Account credit balances are kept out of public material.

## Readiness and error interpretation

The direct client retried chat requests on 503 during startup. One successful request took 161.44 seconds across 24 attempts. The dashboard recorded 71 errors across the whole experiment. Repeated startup/readiness 503s are a plausible major contributor, consistent with the original scripts and Modal's server behavior; the accessible record does not contain a request-by-request breakdown. Do not label the 71 errors as failed generations or publish a generation success rate from this count.

The new client makes readiness probes separately and sends one chat request. Its elapsed reporting distinguishes readiness waiting from the completion request. The completion timer still includes HTTP transport and server processing; it is not pure model decode time or time to first token.

## Generated-answer quality

The original DomainOS prompt elicited an inaccurate description involving edge devices. That response demonstrated serving, while also showing the need to supply authoritative product context and evaluate factual answers. The updated default demonstration prompt asks for a generic explanation of inference and should not be compared as a quality improvement against the original prompt.

## Lab 7 changes and validation

Shared standard-library HTTP code replaces duplicate scripts. It validates endpoint origins, blocks redirects, avoids raw error-body output, limits response size and returns failing status for unexpected results. Authentication checks now include missing and invalid credentials plus a valid-key positive control. Remote CPU/GPU entrypoints require explicit opt-in. Original scripts and their hashes are preserved privately.

The offline regression suite uses loopback HTTP and mocked readiness clocks. See [validation record](validation.md) for actual results. The modified client and shutdown handling were validated locally; the historical cloud results belong to the original scripts. No cloud workload was launched during packaging.

## Next measurement, after separate approval

Use an agreed spending cap and one serialized session. Record the first cold readiness interval, then a fixed number of warm requests using an identical prompt and token cap. Capture timestamps, HTTP status classes, prompt/completion tokens, completion-request duration and resource-active time. Export app-level usage for exactly that window and stop the app immediately afterward.

Calculate warm-request latency percentiles only after sufficient requests. Report cold start separately. Compute `matched compute USD / matched total tokens × 1000`, alongside startup overhead and idle capacity cost. Quote any commercial rate only after adding support, storage, monitoring, network and operating margin to a representative workload model.

# Architecture

I used two serving paths: a local Unsloth API for the quantized GGUF model, and a Modal-hosted vLLM server for the float16 Hugging Face checkpoint.

## Cloud path

The Python client sends an authenticated HTTPS request to Modal. The proxy checks the Proxy Token and routes the request to vLLM. Qwen runs on a T4 and returns chat-completion JSON with generated text and token usage.

![Cloud inference architecture](architecture/cloud.svg)

## Local path

The local Python client calls the authenticated API at `127.0.0.1:8888`. Unsloth serves the Q4_K_M GGUF model through its OpenAI-compatible interface.

![Local Unsloth API path](architecture/local.svg)

## Component responsibilities

Model weights supply the learned parameters. The inference engine executes them. Compute hosts that execution, and the API server connects it to another application.

![Four component responsibilities](architecture/roles.svg)

## Deployment configuration

| Setting | Value in `qwen_vllm.py` |
| --- | --- |
| App | `domainos-qwen-vllm-lab` |
| Server | `QwenServer` |
| Base image / Python | CUDA 12.8.0 devel, Ubuntu 22.04 / Python 3.12 |
| Dependencies | vLLM 0.11.2; huggingface-hub 0.36.0 |
| GPU / CPU / RAM | T4 / 2 / 8192 MiB |
| Model / API alias | `Qwen/Qwen2.5-1.5B-Instruct` / `domainos-qwen` |
| Host / port | `0.0.0.0` / 8000 |
| Numeric type | float16 |
| Context limit | 2048 tokens |
| GPU memory utilization | 0.75 |
| Execution | `--enforce-eager` |
| Cached weights | `domainos-qwen-cache` mounted at `/root/.cache/huggingface` |
| Container limits | minimum 0, maximum 1 |
| Target / hard request concurrency | 1 / 1 |
| Idle scale-down window | 30 seconds |
| Startup timeout | 600 seconds |
| Public unauthenticated access | disabled |

`@modal.enter()` launches vLLM. `@modal.exit()` terminates the subprocess, waits for shutdown, and kills it if it exceeds the shutdown timeout. The model-cache volume persists downloaded weights across container lifetimes.

With zero warm containers, the first authenticated request starts the GPU container. Modal returns 503 until the server is ready. The client handles that interval with bounded readiness polling. [Modal Servers](https://modal.com/docs/guide/servers)

## Diagram sources

The drawings use Virgil handwriting, rough orange connectors and separate light/dark previews. The native scenes contain editable objects and reserve the right side for the presenter. See [diagram sources and rebuild instructions](architecture/README.md).

I keep the complete 26-state progressive presentation in my tutorial library and distribute the seven final diagram states here.

# Getting started

## 1. Local preparation

Start in the lab directory. Use Python 3.12 and a terminal that is not being recorded.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/audit_secrets.py
```

The installed Modal SDK is pinned to the original local version, 1.6.2. vLLM 0.11.2 and huggingface-hub 0.36.0 are installed in the remote image, not on the laptop. The base image tag and model's upstream default revision are mutable; use captured image/model digests when a byte-identical rebuild is required. Their historical digests were not recorded.

## 2. Local Unsloth inference

Open the existing local Unsloth model in its native UI, select the Qwen2.5-1.5B-Instruct Q4_K_M GGUF model, and enable its authenticated OpenAI-compatible API at port 8888. Use the exact model ID returned by your local `/v1/models` if it differs from the original request model below. This repository does not install or launch Unsloth.

```sh
export LOCAL_BASE_URL=http://127.0.0.1:8888
export LOCAL_MODEL=Qwen/Qwen2.5-1.5B-Instruct-GGUF:q4_k_m
python client.py
```

Enter the local API key at the hidden prompt. Expected: HTTP 200, assistant text, token usage if supplied by the local server. Run `python auth_test.py` to test the deliberately invalid local key; expect HTTP 401/403 and a PASS line. The positive request and negative check make the local authentication behavior explicit.

## 3. Modal account setup · private screen

A Modal account with compute access is required. Authentication writes local Modal configuration outside this repository.

```sh
modal setup
```

Create a dedicated Proxy Token in Modal's settings. It is a `wk-` ID and a `ws-` secret. Account API credentials (`ak-` / `as-`) authenticate the developer CLI; they are not the client Proxy Token. Keep creation and copying off camera. See [official proxy authentication](https://modal.com/docs/guide/webhook-proxy-auth).

## 4. Approved cloud checks and deployment · billable

**Run this section only after approval for a live cloud run.** These commands were prepared during Lab 7; no cloud workload was started during packaging.

Optional CPU and T4 checks:

```sh
modal run modal_test.py --allow-cloud
modal run gpu_test.py --allow-cloud
```

Expected CPU result: square of 42 is 1764. Expected GPU result: `nvidia-smi` output identifies a T4. GPU checks run a real billed container.

Deploy:

```sh
modal deploy qwen_vllm.py
```

Copy the returned server origin privately. Do not add `/v1`, a route path, query string or token. Example configuration:

```sh
export ENDPOINT=https://YOUR-SERVER.modal.run
```

Replace the example with the actual returned origin. `.env.example` documents variable names; clients do not automatically load `.env`. Prefer hidden prompts for secrets rather than typing them into shell history. Keep endpoint identity off the public recording.

## 5. Readiness, inference, authentication · explicit live requests

```sh
python readiness_test.py --allow-cloud --wait-ready --readiness-seconds 300
python cloud_client.py --allow-cloud --wait-ready --readiness-seconds 300
python security_test.py --allow-cloud
```

The client and readiness scripts ask for hidden credentials. The authentication script checks missing credentials, deliberately invalid credentials, then a valid-key positive control. Success is HTTP 401/403 for the first two and HTTP 200 with `domainos-qwen` for the positive control. Every unexpected result exits nonzero.

The original test used Bearer `wk-ID.ws-SECRET`; the new client retains that supported format. If unattended execution is required, export `MODAL_PROXY_KEY` and `MODAL_PROXY_SECRET` through a private secret manager. Do not print them, use shell tracing, or include them in command arguments.

A readiness request with valid credentials can start the GPU even though it does not generate text. `--wait-ready` polls only 503 responses and has a 300-second default budget. Without the flag, the readiness script makes one request. Chat POSTs are single submission: after a transport timeout, inspect private logs before manually trying again because generation may have completed remotely.

## 6. Stop and review cost

```sh
modal app stop domainos-qwen-vllm-lab
```

Confirm the CLI stop prompt. Check the dashboard for stopped status and terminated containers, then collect the app's resource usage after billing settles. Stopping the app does not delete its model-cache volume; inspect any remaining storage or other resource charges separately in the account dashboard. Revoke the dedicated Proxy Token after the recording.

## Troubleshooting

| Symptom | Next action |
| --- | --- |
| HTTP 503 | Server is starting or unavailable; use the bounded readiness check, then inspect startup logs privately |
| HTTP 401 | Check Proxy Token ID/secret, not developer account tokens |
| HTTP 403 | Check token environment scope and workspace permissions |
| HTTP 429 | Container concurrency is capped at one; serialize requests |
| Wrong model in `/v1/models` | Confirm endpoint origin and `--served-model-name domainos-qwen` |
| Readiness deadline exceeded | Stop and inspect startup/model loading; do not loop redeployments |
| Local HTTP 401 | Supply the current local API key at the hidden prompt |
| Unexpected redirect or JSON | Check server origin privately; redirects are deliberately blocked |

The runbook follows [Modal Servers](https://modal.com/docs/guide/servers) and the [Modal CLI](https://modal.com/docs/reference/cli/app). Commands and decorator registration were checked locally; a future deployment remains a separately approved cloud action.

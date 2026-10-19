# Getting started

## 1. Set up Python

Use Python 3.12, matching the remote image.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/audit_secrets.py
```

The local dependency is Modal 1.6.2. The remote image installs vLLM 0.11.2 and huggingface-hub 0.36.0. The clients and tests use Python's standard library.

## 2. Run the local Unsloth client

Load Qwen2.5-1.5B-Instruct GGUF in Q4_K_M format in Unsloth. Enable its authenticated OpenAI-compatible API at port 8888.

```sh
export LOCAL_BASE_URL=http://127.0.0.1:8888
export LOCAL_MODEL=Qwen/Qwen2.5-1.5B-Instruct-GGUF:q4_k_m
python client.py
python auth_test.py
```

Enter the local API key at the hidden prompt. The client prints the response and token usage. The negative authentication test expects HTTP 401 or 403. If the model ID differs in your local server, use the ID returned by `/v1/models`.

## 3. Configure Modal

Create a Modal account with compute access, then configure the CLI:

```sh
modal setup
```

Create a dedicated Proxy Token in Modal settings. Its ID begins with `wk-` and its secret with `ws-`. The client sends them as `Authorization: Bearer wk-ID.ws-SECRET`. Developer account tokens authenticate the CLI; Proxy Tokens authenticate requests to the endpoint. [Modal Proxy Tokens](https://modal.com/docs/guide/webhook-proxy-auth)

Keep token creation and copying private. The clients accept exported `MODAL_PROXY_KEY` and `MODAL_PROXY_SECRET` values or hidden prompt input. `.env.example` lists the variable names; export the values in your shell or secret manager.

## 4. Check compute and deploy

These commands use billed cloud compute. `--allow-cloud` is an explicit opt-in for the test scripts.

```sh
modal run modal_test.py --allow-cloud
modal run gpu_test.py --allow-cloud
modal deploy qwen_vllm.py
```

The CPU check returns 1764, the square of 42. The GPU check prints `nvidia-smi` output. Deployment builds the image and creates the authenticated server.

Set the server origin returned by Modal:

```sh
export ENDPOINT=https://YOUR-SERVER.modal.run
```

Use the origin alone, with the scheme and hostname. Keep the private endpoint out of recordings and public files.

## 5. Check readiness and call the API

```sh
python readiness_test.py --allow-cloud --wait-ready --readiness-seconds 300
python cloud_client.py --allow-cloud --wait-ready --readiness-seconds 300
python security_test.py --allow-cloud
```

The readiness check waits for `/v1/models` to return HTTP 200 and `domainos-qwen`. It polls 503 responses within the selected time budget. A valid readiness request can start the GPU container.

The cloud client then submits one chat-completion request and prints its response, usage, completion-request duration and total elapsed time. After a transport timeout, inspect the server logs before submitting another request: the first generation may still be running.

The security check expects rejection for missing and invalid credentials, then confirms valid access to the expected model. Unexpected results return a failing exit status.

## 6. Inspect usage and stop the app

```sh
modal billing report --for today --resolution h --show-resources
modal app stop domainos-qwen-vllm-lab
```

Check the app's Usage page alongside the workspace billing report. Confirm the stop prompt and inspect the stopped state in the dashboard. The latest partial billing interval appears after it closes. The model-cache volume persists after the app stops; review storage separately and revoke the dedicated lab token when finished.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| HTTP 503 | Wait for readiness, then inspect startup logs if the deadline expires |
| HTTP 401 | Check the current Proxy Token ID and secret |
| HTTP 403 | Check token environment scope and workspace permissions |
| HTTP 429 | Serialize requests; concurrency is capped at one |
| Expected model missing | Confirm the endpoint and `--served-model-name domainos-qwen` |
| Local HTTP 401 | Supply the current local API key |
| Redirect or invalid JSON | Check the configured server origin |

See the [experiment report](experiment-report.md) for the captured results and [architecture](architecture.md) for the deployment settings.

"""Standard-library HTTP helpers. Importing this module makes no requests."""
import json
import math
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler

MODEL = "domainos-qwen"
MAX_BODY = 2 * 1024 * 1024

class LabError(Exception):
    pass

class StatusError(LabError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"HTTP {status}")

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def endpoint(value=None, *, local=False):
    value = (value if value is not None else os.getenv("ENDPOINT", "")).rstrip("/")
    p = urlsplit(value)
    if p.username or p.password or p.query or p.fragment or p.path not in ("", "/"):
        raise LabError("Use an origin URL without a path, credentials, query or fragment.")
    try:
        port = p.port
    except ValueError:
        raise LabError("Invalid endpoint port.") from None
    if local:
        if p.scheme != "http" or p.hostname not in ("127.0.0.1", "localhost", "::1"):
            raise LabError("Local API must use HTTP on a loopback host.")
    elif (p.scheme != "https" or not p.hostname or port not in (None,443)
          or not p.hostname.endswith((".modal.run", ".modal.host"))):
        raise LabError("Set ENDPOINT to your HTTPS Modal server origin.")
    return value

def proxy_headers(key, secret):
    if not key.startswith("wk-") or not secret.startswith("ws-"):
        raise LabError("Expected a Modal Proxy Token ID and secret (wk-/ws-).")
    if any(c.isspace() or c in "\r\n" for c in key + secret):
        raise LabError("Credentials contain whitespace.")
    return {"Authorization": f"Bearer {key}.{secret}"}

def request_json(base, path, headers=None, payload=None, timeout=30):
    headers = dict(headers or {})
    headers["Content-Type"] = "application/json"
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(base + path, data=data, headers=headers,
                  method="GET" if data is None else "POST")
    # No redirects or ambient proxies: never forward credentials to another origin.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=timeout) as response:
            status = response.status
            raw = response.read(MAX_BODY + 1)
    except HTTPError as exc:
        status = exc.code
        exc.close()
        raise StatusError(status) from None
    except (URLError, TimeoutError, OSError):
        raise LabError("Network request failed or timed out; inspect connectivity privately.") from None
    if status != 200:
        raise StatusError(status)
    if len(raw) > MAX_BODY:
        raise LabError("Response exceeded size limit.")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise LabError("Server returned invalid JSON.") from None
    if not isinstance(result, dict):
        raise LabError("Expected a JSON object.")
    return result

def require_model(result):
    models = result.get("data")
    if not isinstance(models, list) or not any(
        isinstance(m, dict) and m.get("id") == MODEL for m in models
    ):
        raise LabError("Expected served model is missing from /v1/models.")


def wait_ready(base, headers, *, budget=300, interval=6, clock=time.monotonic,
               sleep=time.sleep, send=request_json):
    if not math.isfinite(budget) or not math.isfinite(interval) or budget <= 0 or interval <= 0:
        raise LabError("Readiness budget and interval must be positive.")
    deadline = clock() + budget
    attempts = 0
    while clock() < deadline:
        attempts += 1
        try:
            result = send(base, "/v1/models", headers, timeout=min(20, max(.1, deadline-clock())))
            require_model(result)
            return attempts
        except StatusError as exc:
            if exc.status != 503:
                raise
        remaining = deadline - clock()
        if remaining > 0:
            sleep(min(interval, remaining))
    raise LabError(f"Readiness deadline exceeded after {attempts} probes.")

def completion(base, headers, *, model=MODEL, prompt="Explain AI inference in one short paragraph.", timeout=120):
    result = request_json(base, "/v1/chat/completions", headers, {
        "model": model, "messages": [{"role":"user", "content":prompt}],
        "max_tokens":150, "temperature":0, "stream":False,
    }, timeout=timeout)
    try:
        text = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LabError("Completion JSON has no assistant message.") from None
    if not isinstance(text,str) or not text.strip():
        raise LabError("Completion message is empty or invalid.")
    usage = result.get("usage", {})
    if not isinstance(usage,dict):
        raise LabError("Invalid usage object.")
    # Print a small allowlist, never the entire raw server response.
    safe_usage = {k:v for k,v in usage.items() if k in
                  ("prompt_tokens","completion_tokens","total_tokens")
                  and isinstance(v,int) and not isinstance(v,bool) and v >= 0}
    return text, safe_usage

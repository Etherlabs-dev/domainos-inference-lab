"""Explicit entrypoints for billable endpoints and the local Unsloth API."""
import argparse
import getpass
import json
import os
import time
from lab_http import (LabError, StatusError, endpoint, proxy_headers,
                      request_json, wait_ready, completion, require_model)

def credentials():
    key = os.getenv("MODAL_PROXY_KEY") or getpass.getpass("Modal Proxy Token ID: ")
    secret = os.getenv("MODAL_PROXY_SECRET") or getpass.getpass("Modal Proxy Secret: ")
    return proxy_headers(key, secret)

def run_cloud(mode="chat"):
    parser = argparse.ArgumentParser(description="DomainOS cloud lab: requests can activate billed compute.")
    parser.add_argument("--allow-cloud", action="store_true", help="Explicitly authorize cloud HTTP requests.")
    if mode != "security":
        parser.add_argument("--wait-ready", action="store_true", help="Poll GET /v1/models on 503 before proceeding.")
        parser.add_argument("--readiness-seconds", type=float, default=300)
    args = parser.parse_args()
    if not args.allow_cloud:
        parser.error("Cloud traffic is disabled. Use --allow-cloud only for an approved live run.")
    try:
        base = endpoint()
        if mode == "security":
            for label, headers in [("missing credentials", {}), ("invalid credentials", {
                "Authorization":"Bearer wk-invalid.ws-invalid"})]:
                try:
                    request_json(base, "/v1/models", headers, timeout=20)
                except StatusError as exc:
                    if exc.status not in (401,403):
                        raise LabError(f"FAIL {label}: unexpected HTTP {exc.status}") from None
                    print(f"PASS {label}: HTTP {exc.status}")
                else:
                    raise LabError(f"FAIL {label}: access accepted")
            # Positive control prevents mistaking an always-denying endpoint for working auth.
            headers = credentials()
            result = request_json(base, "/v1/models", headers, timeout=30)
            require_model(result)
            print("PASS valid credentials: HTTP 200 and expected model")
            return 0
        headers = credentials()
        started = time.monotonic()
        if args.wait_ready:
            count = wait_ready(base, headers, budget=args.readiness_seconds)
            print(f"Ready after {count} probes; wait {time.monotonic()-started:.2f}s")
        if mode == "readiness":
            if not args.wait_ready:
                result = request_json(base, "/v1/models", headers, timeout=20)
                require_model(result)
            print("PASS readiness: HTTP 200 and expected model")
            return 0
        generation_started = time.monotonic()
        text, usage = completion(base, headers)
        print("HTTP 200\nMODEL RESPONSE:\n" + text)
        print("TOKEN USAGE: " + json.dumps(usage, sort_keys=True))
        print(f"Completion request elapsed: {time.monotonic()-generation_started:.2f}s")
        print(f"End-to-end elapsed: {time.monotonic()-started:.2f}s")
        return 0
    except (LabError, EOFError, KeyboardInterrupt) as exc:
        print(str(exc) if isinstance(exc,LabError) else "Cancelled; credentials were not available.")
        return 1

def run_local():
    parser=argparse.ArgumentParser(description="Call an already-running local Unsloth API.")
    parser.parse_args()
    try:
        base=endpoint(os.getenv("LOCAL_BASE_URL","http://127.0.0.1:8888"),local=True)
        key=os.getenv("LOCAL_API_KEY") or getpass.getpass("Local API key: ")
        if not key or any(c.isspace() for c in key):
            raise LabError("Provide a nonempty local API key without whitespace.")
        text, usage=completion(base,{"Authorization":f"Bearer {key}"},model=os.getenv(
            "LOCAL_MODEL","Qwen/Qwen2.5-1.5B-Instruct-GGUF:q4_k_m"))
        print("HTTP 200\nMODEL RESPONSE:\n"+text)
        print("TOKEN USAGE: "+json.dumps(usage,sort_keys=True))
        return 0
    except (LabError,EOFError,KeyboardInterrupt) as exc:
        print(str(exc) if isinstance(exc,LabError) else "Cancelled.")
        return 1


def run_local_security():
    parser = argparse.ArgumentParser(description="Reject a deliberately invalid local API key.")
    parser.parse_args()
    try:
        base = endpoint(os.getenv("LOCAL_BASE_URL", "http://127.0.0.1:8888"), local=True)
        try:
            completion(base, {"Authorization": "Bearer invalid-test-key"}, model=os.getenv(
                "LOCAL_MODEL", "Qwen/Qwen2.5-1.5B-Instruct-GGUF:q4_k_m"))
        except StatusError as exc:
            if exc.status in (401, 403):
                print(f"PASS: deliberately invalid local key rejected with HTTP {exc.status}")
                return 0
            raise
        raise LabError("FAIL: local API accepted a deliberately invalid key.")
    except (LabError, KeyboardInterrupt) as exc:
        print(str(exc) if isinstance(exc, LabError) else "Cancelled.")
        return 1

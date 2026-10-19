# Authentication and secrets

## Access checks

The deployed endpoint returned HTTP 200 with valid credentials and HTTP 401 with a deliberately invalid Proxy Token. The current security script checks missing credentials, invalid credentials and a valid-key positive control.

```sh
python security_test.py --allow-cloud
```

The local negative test uses the fake value `invalid-test-key`:

```sh
python auth_test.py
```

## Credential handling

The clients accept credentials through hidden prompts or exported environment variables. The cloud client uses a Modal Proxy Token ID and secret; Modal developer credentials are used by the deployment CLI.

- Keep real credentials out of source files, shell arguments and recordings.
- Use HTTPS for cloud requests and loopback HTTP for the local API.
- Revoke dedicated lab credentials after use; rotate any credential exposed in a capture.
- Use customer-scoped authorization and isolation for customer deployments.

## HTTP controls

The client validates endpoint origins, blocks redirects, disables ambient proxies, caps response size and checks JSON structure. Error messages expose status codes instead of raw response bodies. Readiness polling handles 503 with an explicit wait flag and a time budget; chat requests are submitted once.

## Repository checks

```sh
python scripts/audit_secrets.py
python scripts/audit_secrets.py --include-private
```

The audit scans source, the Git index, reachable history, reflogs and dangling blobs. It reports file locations and finding categories. Reviewed binary assets are matched by SHA256 against `scripts/reviewed-assets.json`.

Environment files, private originals, editor history, model weights and raw recordings are excluded from Git. Published screenshots are cropped, masked, stripped of metadata and reviewed individually. Keep that review separate from the text scanner, which checks file content and credential patterns.

# DomainOS inference lab

Keep the historical experiment separate from new local validation. See docs/experiment-report.md and evidence/results.json.

- No deployment, cloud HTTP request, Modal run, GPU job, or app restart without explicit user approval for that run.
- Never commit, push or publish without separate approval. Keep Git operations inside this repository.
- Preserve `.private/` and `.history/`; they are excluded private originals, never publication inputs.
- Never expose credentials, endpoint identity, home paths, raw logs or raw screenshots in docs or output.
- Local validation: `python3 -m unittest discover -s tests -v`; `python3 scripts/audit_secrets.py`.
- Update README and docs when behavior changes. Keep the Hugging Face float16 cloud model distinct from the local GGUF model.

- Progressive drawing masters and recording materials live in the canonical content library at `youtube/domainos-managed-inference`. This repo carries final-state distribution snapshots and the pinned renderer only.
- Match the handwritten Virgil/orange/charcoal tutorial style for diagrams; preserve source scenes and prior variants.
- Keep local production drafts out of the public commit. Review the exact staged file list and audit it before every push.

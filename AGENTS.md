# DomainOS inference lab

## Engineering

- Keep the local Unsloth GGUF path distinct from the cloud Hugging Face float16 path.
- Run `python -m unittest discover -s tests -v` and `python scripts/audit_secrets.py` after changes.
- Keep paid cloud execution behind explicit user approval. Deployment, GPU checks and authenticated readiness requests can activate billed compute.
- Commit and push only the scope authorized by the user.
- Preserve private originals and editor history. Keep `.private/`, `.history/`, credentials and raw recordings out of public commits.

## Documentation and visuals

- Write project documentation in my voice: explain what I built, show the result and link the evidence.
- Keep technical constraints concise and tied to a concrete operating consequence.
- Match the handwritten Virgil, orange and charcoal diagram style. Preserve editable sources and previous variants.
- Keep the full progressive-reveal presentation and recording materials in the canonical tutorial library at `youtube/domainos-managed-inference`; this repository contains its engineering companion and final diagram states.
- Review every screenshot individually. Use exact crops and opaque masks, preserve retained pixels, remove metadata, and check the actual export before staging.

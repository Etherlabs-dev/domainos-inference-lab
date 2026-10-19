# Experiment evidence

These four screenshots cover the local API, remote GPU, cloud response, authentication rejection and resource costs from my 19 October 2026 experiment.

| Screenshot | Result shown |
| --- | --- |
| [Cloud inference and authentication](screenshots/cloud-inference-auth.png) | HTTP 200, 42/126/168 tokens, 161.44 seconds and invalid-token HTTP 401 |
| [T4 inspection](screenshots/t4-inspection.png) | NVIDIA Tesla T4 and completed GPU inspection |
| [Local API monitor](screenshots/local-api-monitor.png) | Q4_K_M model loaded, API ready and a completed local request |
| [Resource billing](screenshots/resource-billing.png) | Hourly T4, CPU, memory and network-egress charges |

## Measurements

- [Structured results](results.json)
- [Hourly billing rows](billing-rows.csv)
- [Resource totals](economics.csv)
- [Screenshot manifest](screenshots/manifest.json)
- [Experiment report](../docs/experiment-report.md)

## Image preparation

I kept the originals unchanged and selected tight crops around the results. Published copies remove application chrome, personal prompts, paths, account details and identifiers. Remaining sensitive regions use solid opaque masks. The PNG exports contain the original retained pixels and have their metadata removed.

The manifest records the source and export hashes, crop coordinates and masked regions. I reviewed every export visually and with local OCR before publication.

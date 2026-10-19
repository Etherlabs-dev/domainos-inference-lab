# Tutorial engineering companion

**Deploy an Open-Weight AI Model to the Cloud and Serve It Through an API**

The tutorial follows six phases: explain model/engine/compute/API responsibilities; run local Qwen through Unsloth; verify remote CPU and T4 access; deploy vLLM; call and test the authenticated API; inspect app usage and stop the deployment.

Start with the [deployment runbook](../getting-started.md) for exact commands. Cloud checks require explicit approval and `--allow-cloud`; deployment is a separate deliberate CLI action. Nothing in the tutorial requires automatic deployment or paid CI.

The progressive drawings have seven sections and 26 reveal states: component roles, local API, cloud API, authentication, readiness, economics and recap. This engineering release contains the [seven final diagram states and editable sources](../architecture/README.md). The current recording guide, full reveal master, presentation and three marketing scripts live in the canonical Domain Intelligence Content Library under `youtube/domainos-managed-inference`.

Historical responses and costs are documented in the [experiment report](../experiment-report.md). A future recorded run uses its actual results and date. No inference screenshots or recordings are included in this release.

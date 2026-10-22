# Tutorial: local model to cloud API

[Watch the complete recorded walkthrough on YouTube](https://youtu.be/sbAmuF1waQw).

**Deploy an Open-Weight AI Model to the Cloud and Serve It Through an API**

My tutorial follows six phases:

1. Explain model weights, inference engines, compute and API servers.
2. Run Qwen GGUF locally with Unsloth and call it from Python.
3. Verify remote CPU execution and T4 GPU access.
4. Deploy Qwen with vLLM on Modal.
5. Call the authenticated cloud API and test credential rejection.
6. Inspect resource usage and stop the deployment.

The [deployment guide](../getting-started.md) contains the commands. Cloud checks use `--allow-cloud` because requests can activate billed compute.

The drawings use seven sections and 26 progressive reveal states. This repository includes the [final diagram states, editable sources and renderer](../architecture/README.md). I keep the complete presentation, recording guide and three marketing-video scripts in my Domain Intelligence Content Library under `youtube/domainos-managed-inference`.

The [experiment report](../experiment-report.md) and [screenshots](../../evidence/README.md) accompany the walkthrough.

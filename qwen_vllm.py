import subprocess
import modal

# 1. Define our cloud application
app = modal.App("domainos-qwen-vllm-lab")

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
PORT = 8000

# 2. Define the software environment
image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu22.04",
        add_python="3.12",
    )
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.11.2",
        "huggingface-hub==0.36.0",
    )
)

# 3. Cache downloaded model weights
model_cache = modal.Volume.from_name(
    "domainos-qwen-cache",
    create_if_missing=True,
)

# 4. Define our GPU-backed inference server
@app.server(
    image=image,
    gpu="T4",
    cpu=2,
    memory=8192,
    port=PORT,
    startup_timeout=600,
    min_containers=0,
    max_containers=1,
    target_concurrency=1,
    max_concurrency=1,
    scaledown_window=30,
    unauthenticated=False,
    volumes={
        "/root/.cache/huggingface": model_cache
    },
)
class QwenServer:

    @modal.enter()
    def start(self):
        command = [
            "vllm", "serve", MODEL,
            "--host", "0.0.0.0",
            "--port", str(PORT),
            "--served-model-name", "domainos-qwen",
            "--dtype", "float16",
            "--max-model-len", "2048",
            "--gpu-memory-utilization", "0.75",
            "--enforce-eager",
        ]

        print("Starting DomainOS vLLM server...")
        self.process = subprocess.Popen(command)

    @modal.exit()
    def stop(self):
        print("Stopping DomainOS vLLM server...")
        process = getattr(self, "process", None)
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

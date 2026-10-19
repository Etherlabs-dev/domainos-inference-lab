import modal

app = modal.App("domainos-gpu-test")

@app.function(
    gpu="T4",
    cpu=1,
    memory=512,
    timeout=60,
    min_containers=0,
    max_containers=1,
)
def inspect_gpu():
    import subprocess

    result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        check=True,
    )

    print(result.stdout)
    return "GPU inspection completed"

@app.local_entrypoint()
def main(allow_cloud: bool = False):
    if not allow_cloud:
        raise SystemExit("Cloud execution disabled; add --allow-cloud to run this check.")
    result = inspect_gpu.remote()
    print(result)

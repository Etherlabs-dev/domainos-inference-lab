import modal

# Create a Modal application
app = modal.App("domainos-cloud-test")

# Tell Modal this function runs in the cloud
@app.function()
def square(x):
    print("This code is running on a remote worker!")
    return x ** 2

# This function starts on your Mac
@app.local_entrypoint()
def main(allow_cloud: bool = False):
    if not allow_cloud:
        raise SystemExit("Cloud execution disabled; add --allow-cloud to run this check.")
    result = square.remote(42)
    print("The square is:", result)

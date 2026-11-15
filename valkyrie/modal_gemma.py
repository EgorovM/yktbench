"""Serve the original Gemma weights on one H200 using Modal compute credits."""

import os
import subprocess

import modal


MODEL = "google/gemma-4-31B-it"
REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
# Reuse the tested SGLang image from this workspace's Qwen endpoint.
IMAGE_ID = os.environ.get("YKT_SGLANG_IMAGE_ID", "im-OsQCJKV495m0iTr6LUYlV5")
app = modal.App("ykt-gemma-h200")
cache = modal.Volume.from_name("ykt-gemma-model-cache", create_if_missing=True)


@app.server(
    image=modal.Image.from_id(IMAGE_ID),
    gpu="H200",
    cpu=8,
    memory=32768,
    volumes={"/models": cache},
    env={"HF_HUB_CACHE": "/models/huggingface"},
    port=8000,
    routing_region="us-west",
    startup_timeout=1800,
    min_containers=1,
    max_containers=1,
    target_concurrency=16,
    scaledown_window=300,
)
class Gemma:
    @modal.enter()
    def start(self):
        self.process = subprocess.Popen([
            "python", "-m", "sglang.launch_server",
            "--model-path", MODEL, "--revision", REVISION,
            "--served-model-name", "ykt-gemma-31b",
            "--host", "0.0.0.0", "--port", "8000",
            "--context-length", "65536",
            "--mem-fraction-static", "0.85",
            "--max-running-requests", "16",
            "--enable-metrics",
        ])

    @modal.exit()
    def stop(self):
        self.process.terminate()

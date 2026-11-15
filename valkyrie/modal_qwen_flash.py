"""Serve Qwen Flash's original open weights on four H200 GPUs."""

import os
import subprocess

import modal


MODEL = "Qwen/Qwen3.8-Flash-Next"
REVISION = "812d96e10a0dd82b69d749e68693698cf6c36daa"
IMAGE_ID = os.environ.get("YKT_SGLANG_IMAGE_ID", "im-OsQCJKV495m0iTr6LUYlV5")
app = modal.App("ykt-qwen-flash-h200")
cache = modal.Volume.from_name("ykt-qwen-flash-model-cache", create_if_missing=True)


@app.server(
    image=modal.Image.from_id(IMAGE_ID),
    gpu="H200:4",
    cpu=16,
    memory=65536,
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
class QwenFlash:
    @modal.enter()
    def start(self):
        self.process = subprocess.Popen([
            "python", "-m", "sglang.launch_server",
            "--model-path", MODEL, "--revision", REVISION,
            "--served-model-name", "ykt-qwen-flash",
            "--host", "0.0.0.0", "--port", "8000",
            "--tp", "4", "--context-length", "65536",
            "--mem-fraction-static", "0.85",
            "--max-running-requests", "16",
            "--reasoning-parser", "qwen3", "--enable-metrics",
        ])

    @modal.exit()
    def stop(self):
        self.process.terminate()

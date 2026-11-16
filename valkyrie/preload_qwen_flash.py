"""Complete the pinned Qwen Flash weight cache before starting its GPU server."""

import json
from pathlib import Path

import modal


app = modal.App("ykt-preload-qwen-flash")
cache = modal.Volume.from_name("ykt-qwen-flash-model-cache")
image = modal.Image.debian_slim().pip_install("huggingface_hub")
MODEL = "Qwen/Qwen3.8-Flash-Next"
REVISION = "812d96e10a0dd82b69d749e68693698cf6c36daa"


@app.function(image=image, cpu=8, memory=16384, timeout=1800,
              volumes={"/models": cache},
              env={"HF_HUB_DISABLE_PROGRESS_BARS": "1"})
def preload():
    from huggingface_hub import hf_hub_download, snapshot_download

    folder = Path(snapshot_download(
        MODEL, revision=REVISION, cache_dir="/models/huggingface", max_workers=16,
        allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.tiktoken"],
    ))
    index = json.loads((folder / "model.safetensors.index.json").read_text())
    shards = set(index["weight_map"].values())
    for shard in sorted(shards):
        if not (folder / shard).is_file():
            hf_hub_download(MODEL, shard, revision=REVISION,
                            cache_dir="/models/huggingface", force_download=True)
    missing = [shard for shard in shards if not (folder / shard).is_file()]
    if missing:
        raise RuntimeError(f"Still missing {len(missing)} weight shards")
    cache.commit()
    return {"model": MODEL, "revision": REVISION, "verified_shards": len(shards)}

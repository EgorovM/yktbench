"""Presentation names for models; API identifiers remain in models.toml."""


MODEL_NAMES = {
    "fable-5.2": ("Claude Fable 5.2", "Anthropic"),
    "astra": ("GPT-6 Astra", "OpenAI"),
    "sol-6.1-eval": ("GPT-6.1 Sol", "OpenAI"),
    "sol-6.1": ("GPT-6.1 Sol", "OpenAI"),
    "opus-5.5": ("Claude Opus 5.5", "Anthropic"),
    "gemini-4-argon": ("Gemini 4 Argon", "Google"),
    "gemma-4-31b": ("Gemma 4 31B", "Google"),
    "grok-4.7": ("Grok 4.7", "SpaceX (xAI)"),
    "deepseek-v4": ("DeepSeek V4 Pro", "DeepSeek"),
    "deepseek-v4.1-flash": ("DeepSeek V4.1 Flash", "DeepSeek"),
    "glm-5.3": ("GLM 5.3", "Z.ai"),
    "inkling-flagship": ("Inkling", "Thinking Machines Lab"),
    "inkling-nvfp4": ("Inkling NVFP4", "Thinking Machines Lab"),
    "muse-spark-open": ("Muse Spark Open", "Meta"),
    "kimi-k3.1-pro": ("Kimi K3.1 Pro", "Moonshot AI"),
    "qwen-3.8-2.4t-a95b": ("Qwen3.8 2.4T A95B", "Alibaba"),
    "inkling-2-small": ("Inkling 2 Small", "Thinking Machines Lab"),
    "qwen-3.8-max": ("Qwen3.8 Max", "Alibaba"),
    "qwen-3.8-flash": ("Qwen3.8 Flash", "Alibaba"),
    "qwen-3.8-27b": ("Qwen3.8 27B", "Alibaba"),
    "gigachat-3.5": ("GigaChat 3.5 Ultra", "Sber"),
    "mock": ("Mock (offline)", "—"),
}


def model_name(alias):
    return MODEL_NAMES.get(alias, (alias, "—"))[0]


def model_company(alias):
    return MODEL_NAMES.get(alias, (alias, "—"))[1]

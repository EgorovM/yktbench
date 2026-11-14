"""One `complete()` call per model, whatever the vendor.

Each provider takes a system prompt and a user message (and optionally a JSON schema the
reply must follow) and returns a Completion. Retries for 429/5xx/connection errors are
left to the vendor SDKs (max_retries below).
"""

import json
import os
import re
import time
from dataclasses import dataclass, field


@dataclass
class Completion:
    text: str
    served_by: str = ""            # model that actually produced the text
    stop_reason: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_s: float = 0.0
    extra: dict = field(default_factory=dict)


def make_provider(name, cfg):
    kind = cfg.get("provider")
    if kind == "anthropic":
        return AnthropicProvider(name, cfg)
    if kind == "openai_responses":
        return OpenAIResponsesProvider(name, cfg)
    if kind == "openai_chat":
        return OpenAIChatProvider(name, cfg)
    if kind == "mock":
        return MockProvider(name, cfg)
    raise ValueError(f"model {name!r}: unknown provider {kind!r}")


def _api_key(cfg, name):
    env = cfg.get("api_key_env")
    if not env:
        return None
    key = os.environ.get(env)
    if not key:
        raise RuntimeError(f"model {name!r}: environment variable {env} is not set")
    return key


class AnthropicProvider:
    FALLBACK_BETA = "server-side-fallback-2026-07-01"

    def __init__(self, name, cfg):
        import anthropic

        self.name, self.cfg = name, cfg
        # No api_key argument: the SDK reads ANTHROPIC_API_KEY or an `ant auth login` profile.
        self.client = anthropic.Anthropic(max_retries=cfg.get("max_retries", 6))

    def complete(self, system, user, schema=None):
        cfg = self.cfg
        kwargs = dict(
            model=cfg["model"],
            max_tokens=cfg.get("max_tokens", 32000),
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        output_config = {}
        if cfg.get("effort"):
            output_config["effort"] = cfg["effort"]
        if schema:
            output_config["format"] = {"type": "json_schema", "schema": schema}
        if output_config:
            kwargs["output_config"] = output_config

        t0 = time.monotonic()
        # Streaming so long reasoning turns don't hit HTTP timeouts.
        if cfg.get("fallbacks", False):
            with self.client.beta.messages.stream(
                **kwargs, betas=[self.FALLBACK_BETA], fallbacks="default"
            ) as stream:
                msg = stream.get_final_message()
        else:
            with self.client.messages.stream(**kwargs) as stream:
                msg = stream.get_final_message()
        latency = time.monotonic() - t0

        text = "".join(b.text for b in msg.content if b.type == "text")
        iterations = getattr(msg.usage, "iterations", None) or []
        fallback_ran = any(getattr(it, "type", None) == "fallback_message" for it in iterations)
        extra = {"request_id": getattr(msg, "_request_id", None), "fallback_ran": fallback_ran}
        if msg.stop_reason == "refusal" and getattr(msg, "stop_details", None):
            extra["refusal_category"] = msg.stop_details.category
        return Completion(
            text=text,
            served_by=msg.model,
            stop_reason=msg.stop_reason or "",
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            latency_s=latency,
            extra=extra,
        )


class OpenAIResponsesProvider:
    def __init__(self, name, cfg):
        import openai

        self.name, self.cfg = name, cfg
        self.client = openai.OpenAI(
            api_key=_api_key(cfg, name),
            base_url=cfg.get("base_url") or None,
            max_retries=cfg.get("max_retries", 6),
            timeout=cfg.get("timeout", 900),
        )

    def complete(self, system, user, schema=None):
        cfg = self.cfg
        kwargs = dict(
            model=cfg["model"],
            instructions=system,
            input=user,
            max_output_tokens=cfg.get("max_tokens", 32000),
        )
        if cfg.get("effort"):
            kwargs["reasoning"] = {"effort": cfg["effort"]}
        if schema:
            kwargs["text"] = {"format": {"type": "json_schema", "name": "grade", "schema": schema, "strict": True}}
        t0 = time.monotonic()
        r = self.client.responses.create(**kwargs)
        latency = time.monotonic() - t0
        stop = r.status or ""
        if r.status == "incomplete" and r.incomplete_details:
            stop = f"incomplete:{r.incomplete_details.reason}"
        usage = r.usage
        return Completion(
            text=r.output_text or "",
            served_by=r.model,
            stop_reason=stop,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            latency_s=latency,
            extra={"response_id": r.id},
        )


class OpenAIChatProvider:
    def __init__(self, name, cfg):
        import openai

        self.name, self.cfg = name, cfg
        self.client = openai.OpenAI(
            api_key=_api_key(cfg, name),
            base_url=cfg.get("base_url") or None,
            max_retries=cfg.get("max_retries", 6),
            timeout=cfg.get("timeout", 900),
        )

    def complete(self, system, user, schema=None):
        cfg = self.cfg
        kwargs = dict(
            model=cfg["model"],
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=cfg.get("max_tokens", 32000),
        )
        if cfg.get("extra_body"):
            kwargs["extra_body"] = cfg["extra_body"]
        if schema and cfg.get("json_mode", False):
            kwargs["response_format"] = {"type": "json_object"}
        t0 = time.monotonic()
        r = self.client.chat.completions.create(**kwargs)
        latency = time.monotonic() - t0
        choice = r.choices[0]
        usage = r.usage
        return Completion(
            text=choice.message.content or "",
            served_by=r.model or cfg["model"],
            stop_reason=choice.finish_reason or "",
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
            latency_s=latency,
            extra={"response_id": r.id},
        )


class MockProvider:
    """Offline stand-in. As a solver it answers from the answer key for about half the
    items (by a hash of the instruction) and says "I don't know" otherwise. As a judge it
    compares normalised strings part by part. Only for checking the pipeline end to end."""

    def __init__(self, name, cfg):
        self.name, self.cfg = name, cfg
        from pathlib import Path

        path = Path(__file__).parent / "data" / "ykt_sample.jsonl"
        self.items = [json.loads(line) for line in path.open(encoding="utf-8")]

    @staticmethod
    def _norm(s):
        return re.sub(r"[^\w]+", " ", s.lower()).strip()

    @staticmethod
    def _parts(s):
        parts = [p for p in re.split(r"\s*\d+[.)]\s*", s) if p.strip()]
        return parts or [s]

    def complete(self, system, user, schema=None):
        if schema:  # judge
            ref = re.search(r"## Reference answer[^\n]*\n(.*?)\n\n## Candidate", user, re.S).group(1)
            cand = user.split("## Candidate answer\n", 1)[1]
            cn = self._norm(cand)
            parts = [
                {"reference": p.strip(), "candidate": "", "correct": self._norm(p) in cn and bool(self._norm(p))}
                for p in self._parts(ref)
            ]
            return Completion(text=json.dumps({"parts": parts, "reason": "mock string match"}), served_by="mock")
        import zlib

        for it in self.items:
            if it["instruction"] in user and it["content"] in user:
                if zlib.crc32(it["id"].encode()) % 2 == 0:
                    return Completion(text=f"Бу таабырын.\nХОРУЙ: {it['answer']}", served_by="mock")
                break
        return Completion(text="Билбэтим.\nХОРУЙ: билбэтим", served_by="mock")

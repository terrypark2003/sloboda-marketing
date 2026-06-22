"""Gemini backend: the CMO's brain on Google's Gemini API.

Mirrors ``claude_client.generate()`` so the bot stays provider-agnostic. History
items use ``{"role": "user"|"model", "content": <text>}``. Google Search
grounding gives the CMO live market data (the equivalent of Claude's web_search).
"""

from __future__ import annotations

import logging

from google import genai
from google.genai import types

from . import config
from .brand import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _to_contents(history: list[dict]) -> list[types.Content]:
    contents: list[types.Content] = []
    for msg in history:
        role = "model" if msg.get("role") in ("assistant", "model") else "user"
        text = msg.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    return contents


def _build_config() -> types.GenerateContentConfig:
    kwargs: dict = {
        "system_instruction": SYSTEM_PROMPT,
        "max_output_tokens": config.MAX_TOKENS,
    }
    if config.ENABLE_WEB_SEARCH:
        # Google Search grounding — the CMO's live market-research tool.
        kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    if not config.ENABLE_THINKING:
        # Disable thinking to cut cost (supported on Flash / Flash-Lite tiers).
        kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    return types.GenerateContentConfig(**kwargs)


def generate(history: list[dict]) -> tuple[str, list[dict], str]:
    """Run one CMO turn on Gemini. Same signature/contract as claude_client.generate."""
    response = _get_client().models.generate_content(
        model=config.GEMINI_MODEL,
        contents=_to_contents(history),
        config=_build_config(),
    )
    try:
        text = (response.text or "").strip()
    except Exception:  # noqa: BLE001 — blocked/empty responses can raise on .text
        text = ""

    new_history = list(history)
    if text:
        new_history.append({"role": "model", "content": text})
    return text, new_history, "stop"

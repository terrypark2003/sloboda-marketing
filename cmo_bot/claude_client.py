"""Claude wrapper: the CMO's brain.

Uses the configured Claude model (CMO_MODEL; default Opus 4.8) with the
server-side web_search tool so market research is grounded in current data.
Adaptive thinking and the search-tool variant are auto-selected by model, so
switching CMO_MODEL to Sonnet 4.6 or Haiku 4.5 just works. Runs synchronously —
the bot calls it from a worker thread so the async event loop stays responsive.
"""

from __future__ import annotations

import logging

import anthropic

from . import config
from .brand import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(
    api_key=config.ANTHROPIC_API_KEY,
    timeout=config.REQUEST_TIMEOUT,
)


# Models that support adaptive thinking + the dynamic-filtering web_search variant
# (the 4.6+ tiers). Other models (e.g. Haiku 4.5, Sonnet 4.5) fall back to the
# basic web_search variant and no thinking — so any CMO_MODEL value just works.
_ADAPTIVE_MODELS = (
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-fable-5",
    "claude-mythos-5",
)


def _supports_adaptive(model: str) -> bool:
    return any(model.startswith(m) for m in _ADAPTIVE_MODELS)


def _tools() -> list[dict]:
    if not config.ENABLE_WEB_SEARCH:
        return []
    # Dynamic-filtering variant on 4.6+ tiers; basic variant elsewhere (Haiku 4.5, etc.)
    web_search_type = (
        "web_search_20260209" if _supports_adaptive(config.MODEL) else "web_search_20250305"
    )
    return [
        {
            "type": web_search_type,
            "name": "web_search",
            "max_uses": config.WEB_SEARCH_MAX_USES,
            "user_location": {
                "type": "approximate",
                "country": "KR",
                "timezone": "Asia/Seoul",
            },
        }
    ]


def _thinking() -> dict | None:
    if not config.ENABLE_THINKING or not _supports_adaptive(config.MODEL):
        return None
    return {"type": "adaptive"}


def _extract_text(content) -> str:
    parts = [block.text for block in content if getattr(block, "type", None) == "text"]
    return "\n".join(p for p in parts if p).strip()


def generate(
    history: list[dict],
    extra_context: str | None = None,
    image: tuple[bytes, str] | None = None,  # noqa: ARG001 — images are Gemini-only for now
) -> tuple[str, list[dict], str]:
    """Run one CMO turn.

    Args:
        history: full conversation, ending with the latest user message.
        extra_context: appended to the system prompt (e.g. team data notes).
        image: accepted for interface parity; not supported on this backend.

    Returns:
        (reply_text, updated_history, stop_reason). ``updated_history`` includes
        the assistant turn(s) produced this call and should replace the caller's
        stored history.
    """
    system = SYSTEM_PROMPT if not extra_context else f"{SYSTEM_PROMPT}\n\n{extra_context}"
    messages = list(history)
    kwargs: dict = {
        "model": config.MODEL,
        "max_tokens": config.MAX_TOKENS,
        "system": system,
        "messages": messages,
    }
    tools = _tools()
    if tools:
        kwargs["tools"] = tools
    thinking = _thinking()
    if thinking:
        kwargs["thinking"] = thinking

    # Server-side tools (web_search) may return stop_reason="pause_turn" when the
    # internal tool loop hits its iteration cap. Re-send to let it resume.
    for _ in range(6):
        response = _client.messages.create(**kwargs)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "pause_turn":
            continue
        break

    return _extract_text(response.content), messages, response.stop_reason

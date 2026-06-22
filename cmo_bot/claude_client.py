"""Claude wrapper: the CMO's brain.

Uses Claude Opus 4.8 with adaptive thinking and the server-side web_search tool
so market research is grounded in current data. Runs synchronously — the bot
calls it from a worker thread so the async event loop stays responsive.
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


def _tools() -> list[dict]:
    if not config.ENABLE_WEB_SEARCH:
        return []
    return [
        {
            "type": "web_search_20260209",
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
    return {"type": "adaptive"} if config.ENABLE_THINKING else None


def _extract_text(content) -> str:
    parts = [block.text for block in content if getattr(block, "type", None) == "text"]
    return "\n".join(p for p in parts if p).strip()


def generate(history: list[dict]) -> tuple[str, list[dict], str]:
    """Run one CMO turn.

    Args:
        history: full conversation, ending with the latest user message.

    Returns:
        (reply_text, updated_history, stop_reason). ``updated_history`` includes
        the assistant turn(s) produced this call and should replace the caller's
        stored history.
    """
    messages = list(history)
    kwargs: dict = {
        "model": config.MODEL,
        "max_tokens": config.MAX_TOKENS,
        "system": SYSTEM_PROMPT,
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

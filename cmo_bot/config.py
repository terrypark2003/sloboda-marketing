"""Runtime configuration, loaded from environment / .env."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_set(name: str) -> set[int]:
    """Parse a comma/space/semicolon-separated list of integers from env."""
    raw = os.getenv(name, "")
    ids: set[int] = set()
    for part in raw.replace(";", ",").replace(" ", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            pass
    return ids


TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Which LLM provider powers the CMO: "gemini" (default, cheaper) or "anthropic".
PROVIDER: str = os.getenv("CMO_PROVIDER", "gemini").strip().lower()

# Anthropic (Claude) — used when CMO_PROVIDER=anthropic
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODEL: str = os.getenv("CMO_MODEL", "claude-opus-4-8").strip()

# Google Gemini — used when CMO_PROVIDER=gemini
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL: str = os.getenv("CMO_GEMINI_MODEL", "gemini-2.5-flash").strip()

MAX_TOKENS: int = int(os.getenv("CMO_MAX_TOKENS", "8000"))
REQUEST_TIMEOUT: float = float(os.getenv("CMO_REQUEST_TIMEOUT", "300"))

ENABLE_WEB_SEARCH: bool = _flag("CMO_ENABLE_WEB_SEARCH", True)
ENABLE_THINKING: bool = _flag("CMO_ENABLE_THINKING", True)

# How many messages of conversation memory to keep per chat (trimmed from the
# oldest). One user turn + one assistant turn = 2 messages.
HISTORY_MAX_MESSAGES: int = int(os.getenv("CMO_HISTORY_MAX_MESSAGES", "24"))

# Max server-side web searches Claude may run per turn (cost guard).
WEB_SEARCH_MAX_USES: int = int(os.getenv("CMO_WEB_SEARCH_MAX_USES", "5"))

# Allowlist of Telegram chat IDs permitted to use the CMO (protects API budget).
# Empty = open to anyone who finds the bot. Each user can get their own ID via /id.
ALLOWED_CHAT_IDS: set[int] = _int_set("CMO_ALLOWED_CHAT_IDS")


def active_model() -> str:
    """The model string for the selected provider (for logging/UX)."""
    return GEMINI_MODEL if PROVIDER == "gemini" else MODEL


def validate() -> None:
    """Raise a friendly error if required secrets are missing."""
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
    elif not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if missing:
        raise SystemExit(
            f"환경 변수가 설정되지 않았습니다 (provider={PROVIDER}): "
            + ", ".join(missing)
            + "\n.env.example 파일을 .env로 복사한 뒤 값을 채워 주세요."
        )

"""Provider dispatcher — picks the CMO backend from CMO_PROVIDER.

Only the selected backend is imported, so you don't need the other provider's
SDK or API key installed/set.
"""

from __future__ import annotations

from . import config

if config.PROVIDER == "anthropic":
    from .claude_client import generate
else:
    from .gemini_client import generate

__all__ = ["generate"]

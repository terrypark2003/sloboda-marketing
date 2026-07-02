"""Naver Open API lookups — live Korean market data for the CMO.

Google-grounded search can't see Naver Shopping rankings, competitor counts, or
prices — the data that actually decides Smart Store exposure. This module pulls
them directly. Enabled when NAVER_CLIENT_ID / NAVER_CLIENT_SECRET are set
(free keys: https://developers.naver.com/apps/).
"""

from __future__ import annotations

import html
import re

import httpx

from . import config

_API = "https://openapi.naver.com/v1/search/{kind}.json"
_TAG_RE = re.compile(r"<[^>]+>")


def available() -> bool:
    return bool(config.NAVER_CLIENT_ID and config.NAVER_CLIENT_SECRET)


def _clean(text: str) -> str:
    return html.unescape(_TAG_RE.sub("", text or "")).strip()


def _get(kind: str, query: str, display: int = 10, sort: str = "sim") -> dict:
    resp = httpx.get(
        _API.format(kind=kind),
        params={"query": query, "display": display, "sort": sort},
        headers={
            "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def market_snapshot(query: str) -> str:
    """Fetch a compact text snapshot of the Naver market for ``query``.

    Returned text is fed to the LLM as ground truth, so keep it factual and
    compact: shopping totals + top listings (price/mall/brand) and recent blog
    titles (what consumers are talking about).
    """
    shop = _get("shop", query, display=10)
    blog = _get("blog", query, display=5, sort="date")

    lines = [f'[네이버 실시간 데이터 — 검색어 "{query}"]']
    lines.append(f"■ 네이버쇼핑 등록 상품 수: {shop.get('total', 0):,}개")
    lines.append("■ 쇼핑 상위 노출 상품:")
    for i, item in enumerate(shop.get("items", []), 1):
        title = _clean(item.get("title", ""))
        price = int(item.get("lprice") or 0)
        mall = item.get("mallName", "")
        brand = item.get("brand") or item.get("maker") or ""
        extra = f" / {brand}" if brand else ""
        lines.append(f"{i}. {title} — {price:,}원 ({mall}{extra})")
    lines.append("■ 최신 블로그 글(소비자 관심사):")
    for item in blog.get("items", []):
        lines.append(f"- {_clean(item.get('title', ''))} ({item.get('postdate', '')})")
    return "\n".join(lines)

"""The inline "explore marketing options" menu.

Each button maps to a preset user-style prompt that is fed to the CMO, so the
team can explore common marketing moves with one tap.
"""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# callback_data -> (button label, preset prompt sent to the CMO)
OPTIONS: dict[str, tuple[str, str]] = {
    "campaign": (
        "🎯 인지도 캠페인",
        "브랜드 인지도를 높이기 위한 캠페인 아이디어를 3가지 제안해줘. "
        "각 채널(병원/스마트스토어/와디즈)에 맞춰서, 저예산으로 빠르게 테스트할 수 있는 안으로.",
    ),
    "research": (
        "🔍 시장·경쟁 조사",
        "슬로보다가 속한 시장(시카·병풀 재생/장벽 크림, 더마코스메틱 재생크림)을 조사해줘. "
        "현재 주요 경쟁 제품과 가격대, 소비자가 중요하게 보는 포인트, 최근 트렌드를 최신 정보로 정리해줘.",
    ),
    "target": (
        "👥 타깃·고객 분석",
        "우리 핵심 타깃 고객을 2~3개의 페르소나로 정의해줘. "
        "각 페르소나가 어디서 정보를 얻고, 무엇 때문에 구매하고, 무엇 때문에 망설이는지 분석해줘.",
    ),
    "channel": (
        "🛒 채널 전략",
        "병원 / 네이버 스마트스토어 / 와디즈 3개 채널 각각의 역할과 우선순위, 채널별 핵심 전술을 정리해줘. "
        "지금 신생 브랜드 단계에서 어디에 집중해야 할지 추천도 함께.",
    ),
    "content": (
        "✍️ 콘텐츠·카피",
        "스마트스토어 상세페이지와 SNS에서 쓸 핵심 메시지와 카피 방향을 잡아줘. "
        "'자극지수 0.00, 병풀 500,000ppm, 매일 쓰는 장벽 크림' 강점을 살린 광고 헤드라인 예시 5개도 줘.",
    ),
    "data": (
        "📊 성과 지표(KPI)",
        "마케팅 성과를 측정하기 위해 채널별로 어떤 지표(KPI)를 봐야 하는지 정리해줘. "
        "그리고 내가 매주 5분 안에 확인할 수 있는 간단한 대시보드 항목을 알려줘.",
    ),
    "plan30": (
        "🗓️ 30일 실행 플랜",
        "지금부터 30일 동안 실행할 수 있는 마케팅 액션 플랜을 주차별로 짜줘. "
        "와디즈 펀딩 성공과 스마트스토어 전환을 우선순위로.",
    ),
    "wadiz": (
        "🚀 와디즈 펀딩",
        "와디즈 펀딩(캠페인 #408720)을 성공시키기 위한 실행 가이드를 줘. "
        "오픈 전 알림신청 모으기, 리워드 구성, 펀딩 페이지 메시지, 오픈 첫날 전략까지 단계별로.",
    ),
}


def keyboard() -> InlineKeyboardMarkup:
    """Two buttons per row."""
    keys = list(OPTIONS.keys())
    rows = []
    for i in range(0, len(keys), 2):
        row = [
            InlineKeyboardButton(OPTIONS[k][0], callback_data=k)
            for k in keys[i : i + 2]
        ]
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def preset(callback_data: str) -> str | None:
    item = OPTIONS.get(callback_data)
    return item[1] if item else None


def label(callback_data: str) -> str | None:
    item = OPTIONS.get(callback_data)
    return item[0] if item else None

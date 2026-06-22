# 슬로보다 CMO (Chief Marketing Officer) 텔레그램 봇

슬로보다(SLOBODA)의 **AI 마케팅 책임자**를 텔레그램 봇으로 만든 프로젝트입니다.
Claude(Opus 4.8)가 우리 브랜드와 시장을 이해한 상태에서, 대화하며 마케팅 옵션을
함께 탐구하고 실행 계획을 만들어 줍니다.

목표는 명확합니다 — **재생크림(No.7 리커버리 크림)을 마케팅으로 판다.**
판매 채널은 **① 병원 ② 네이버 스마트스토어 ③ 와디즈 펀딩** 입니다.

## CMO가 하는 일

- 🎯 **마케팅·브랜드 전략 수립** — 신생 브랜드 / 저예산 가정, 실행 가능한 선택지 제시
- 🔍 **시장 조사 & 고객 분석** — `web_search`로 경쟁사·트렌드·검색 흐름을 **최신 데이터**로 조사
- 📣 **브랜드 인지도 캠페인 기획** — 채널별 캠페인·콘텐츠·30일 실행 플랜

CMO는 다음 브랜드 사실을 이미 알고 있습니다 (출처: 네이버 스마트스토어, 와디즈 캠페인 #408720, 블로그 리뷰):

- 대표 제품: **슬로보다 No.7 리커버리 크림** (재생 콘셉트의 데일리 장벽 케어 크림)
- 핵심 성분: **병풀잎수(시카) 500,000ppm**
- 차별점: **자극지수 0.00**, 일반·민감성 피부 일차자극 인체적용시험 완료
- 가격: 스마트스토어 약 **43,000원**
- 콘셉트: "단계를 늘리기보다 매일 바르는 크림 하나로"

> 브랜드 정보가 바뀌면 `cmo_bot/brand.py`만 수정하면 됩니다. (CMO 지식의 단일 출처)

## 빠르게 시작하기

### 1) 텔레그램 봇 토큰 만들기
1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색 → `/newbot`
2. 봇 이름과 사용자명을 정하면 **토큰**(`123456789:ABC...`)을 줍니다.

### 2) Anthropic API 키 발급
- <https://console.anthropic.com/> 에서 API 키(`sk-ant-...`) 발급

### 3) 설치 & 실행
```bash
git clone <this-repo>
cd sloboda-marketing

python -m venv .venv && source .venv/bin/activate   # (선택) 가상환경
pip install -r requirements.txt

cp .env.example .env        # .env 파일에 토큰/키 입력
# TELEGRAM_BOT_TOKEN=...
# ANTHROPIC_API_KEY=...

python run.py
```
봇이 실행되면 텔레그램에서 내 봇을 찾아 `/start` 를 눌러 보세요.

## 사용법

- 그냥 메시지를 보내면 마케팅 전략으로 답합니다.
  - 예) "와디즈 펀딩 목표 금액 어떻게 잡을까?", "스마트스토어 첫 리뷰 30개 모으는 법"
- `/menu` — 자주 쓰는 마케팅 옵션 버튼 (인지도 캠페인 · 시장 조사 · 타깃 분석 · 채널 전략 · 콘텐츠/카피 · KPI · 30일 플랜 · 와디즈)
- `/reset` — 대화 맥락 초기화
- `/help` — 도움말

> 💡 **매출·방문수·전환율·광고비·리뷰 수** 같은 숫자를 알려 주면 훨씬 구체적인 조언을 받을 수 있어요.

## 환경 변수 (`.env`)

| 변수 | 필수 | 기본값 | 설명 |
|------|:----:|--------|------|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | BotFather 토큰 |
| `ANTHROPIC_API_KEY` | ✅ | — | Anthropic API 키 |
| `CMO_MODEL` | | `claude-opus-4-8` | 사용할 Claude 모델 |
| `CMO_MAX_TOKENS` | | `8000` | 답변 최대 토큰 |
| `CMO_ENABLE_WEB_SEARCH` | | `true` | 실시간 시장 조사(web_search) 사용 |
| `CMO_ENABLE_THINKING` | | `true` | 적응형 사고(adaptive thinking) 사용 |
| `CMO_HISTORY_MAX_MESSAGES` | | `24` | 대화 메모리 길이 |
| `CMO_REQUEST_TIMEOUT` | | `300` | API 요청 타임아웃(초) |

## 구조

```
run.py                  # 진입점
cmo_bot/
  config.py             # 환경 변수 / 설정
  brand.py              # 브랜드 지식 + CMO 시스템 프롬프트 (지식의 단일 출처)
  menu.py               # 인라인 "마케팅 옵션" 메뉴
  claude_client.py      # Claude 호출 (adaptive thinking + web_search)
  bot.py                # 텔레그램 핸들러 / 메모리 / 메시지 분할
requirements.txt
.env.example
```

## 동작 방식 (간단히)

`bot.py`가 텔레그램 메시지를 받아 채팅별 대화 기록에 쌓고, 워커 스레드에서
`claude_client.generate()`를 호출합니다. Claude는 `brand.py`의 CMO 시스템
프롬프트로 역할을 부여받고, 필요 시 `web_search` 서버 도구로 최신 시장 정보를
직접 조사한 뒤 답합니다. 답변은 텔레그램 길이에 맞게 분할되어 전송됩니다.

## 비용 메모

- 대화·시장 조사 한 번에 Claude API 토큰이 소모됩니다(특히 `web_search` 사용 시).
- 비용을 줄이려면 `CMO_ENABLE_WEB_SEARCH=false` 또는 `CMO_MODEL=claude-sonnet-4-6`로
  바꿀 수 있습니다.

## 운영 메모

- 봇은 폴링 방식으로 동작하므로 **항상 켜져 있는 환경**(개인 서버, 작은 VM, 라즈베리파이 등)에서
  `python run.py`로 띄워 두면 됩니다.
- 대화 메모리는 메모리(in-memory)에 저장되며 봇을 재시작하면 초기화됩니다.
- 시크릿(`.env`)은 절대 깃에 커밋하지 마세요. (`.gitignore`에 이미 포함)

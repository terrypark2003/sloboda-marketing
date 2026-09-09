# 슬로보다 CMO (Chief Marketing Officer) 텔레그램 봇

슬로보다(SLOBODA)의 **AI 마케팅 책임자**를 텔레그램 봇으로 만든 프로젝트입니다.
**Google Gemini**(기본) 또는 Claude가 우리 브랜드와 시장을 이해한 상태에서, 대화하며
마케팅 옵션을 함께 탐구하고 실행 계획을 만들어 줍니다. 제공사는 `.env`의 `CMO_PROVIDER`로
고릅니다(`gemini` 기본, `anthropic` 선택).

목표는 명확합니다 — **재생크림(No.7 리커버리 크림)을 마케팅으로 판다.**
판매 채널은 **① 병원 ② 네이버 스마트스토어 ③ 와디즈 펀딩** 입니다.

## CMO가 하는 일

- 🎯 **마케팅·브랜드 전략 수립** — 신생 브랜드 / 저예산 가정, 실행 가능한 선택지 제시
- 🔍 **시장 조사 & 고객 분석** — 실시간 웹검색(Gemini=Google 검색 그라운딩 / Claude=web_search)으로 경쟁사·트렌드를 **최신 데이터**로 조사
- 📣 **브랜드 인지도 캠페인 기획** — 채널별 캠페인·콘텐츠·30일 실행 플랜
- 📝 **데이터 노트** (`/note`) — 팀이 기록한 실데이터(방문수·전환율·펀딩 현황)를 **모든 답변에 반영**
- 📸 **이미지 분석** — 상세페이지·광고 시안·경쟁사 화면 스크린샷을 보내면 피드백
- ⏰ **주간 CMO 브리핑** (`/briefing on`) — 매주 월요일 아침, 시장 동향 + 이번 주 액션을 먼저 보고
- 🛒 **네이버 실데이터 조회** (`/naver 키워드`) — 네이버 쇼핑 등록 상품 수·상위 노출·가격대를 실시간 조회 후 분석 (무료 네이버 API 키 필요)
- 💾 **영구 메모리** — 대화·노트가 디스크에 저장되어 재시작에도 유지 (Railway는 볼륨 연결 시)

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

### 2) Gemini API 키 발급 (기본 제공사)
- <https://aistudio.google.com/apikey> 에서 API 키(`AIza...`) 발급 (무료 티어 있음)
- (Claude를 쓰려면 대신 <https://console.anthropic.com/> 에서 키 발급 후 `CMO_PROVIDER=anthropic`)

### 3) 설치 & 실행
```bash
git clone <this-repo>
cd sloboda-marketing

python -m venv .venv && source .venv/bin/activate   # (선택) 가상환경
pip install -r requirements.txt

cp .env.example .env        # .env 파일에 토큰/키 입력
# TELEGRAM_BOT_TOKEN=...
# CMO_PROVIDER=gemini
# GEMINI_API_KEY=AIza...

python run.py
```
봇이 실행되면 텔레그램에서 내 봇을 찾아 `/start` 를 눌러 보세요.

## 사용법

- 그냥 메시지를 보내면 마케팅 전략으로 답합니다.
  - 예) "와디즈 펀딩 목표 금액 어떻게 잡을까?", "스마트스토어 첫 리뷰 30개 모으는 법"
- `/menu` — 자주 쓰는 마케팅 옵션 버튼 (인지도 캠페인 · 시장 조사 · 타깃 분석 · 채널 전략 · 콘텐츠/카피 · KPI · 30일 플랜 · 와디즈)
- `/note 내용` — 데이터 노트 기록 (예: `/note 지난주 방문 1,200명, 전환율 1.1%`) · `/notes` 목록 · `/delnote 번호` 삭제
- `/briefing on|off|now` — 주간 CMO 브리핑 (매주 월요일 오전 9시 KST, `now`로 즉시 받기)
- `/naver 키워드` — 네이버 쇼핑 실시간 경쟁 데이터 조회 + 분석
- 📸 사진 전송 — 상세페이지/광고 시안/경쟁사 화면 분석 (캡션에 질문을 쓰면 그에 맞춰 답변)
- `/reset` — 대화 맥락 초기화 (노트는 유지)
- `/id` — 이 채팅의 chat ID 확인 (허용 목록 등록용)
- `/help` — 도움말

그룹 채팅에서는 봇을 **@멘션**하거나 봇 메시지에 **답장**할 때만 응답해요. (그룹 chat ID도 `/id`로 확인해 허용 목록에 추가)

> 💡 **매출·방문수·전환율·광고비·리뷰 수** 같은 숫자를 알려 주면 훨씬 구체적인 조언을 받을 수 있어요.

## 🔑 토큰은 어디에 연결하나요?

봇 토큰과 API 키는 **코드가 아니라 `.env` 파일**에 넣습니다. (깃에 커밋되지 않음)

```bash
cp .env.example .env
```
그리고 `.env`를 열어 채우세요 (기본 = Gemini):
```dotenv
TELEGRAM_BOT_TOKEN=123456789:AA....   # BotFather가 준 토큰
CMO_PROVIDER=gemini
GEMINI_API_KEY=AIza....               # Google AI Studio 키
```
> ⚠️ **토큰/키는 채팅·깃·캡처로 공유하지 마세요.** 노출되면 즉시 재발급(@BotFather `/revoke`, 키 발급처에서 삭제)하세요. `.env`는 운영하는 서버에만 둡니다.
> (Railway 같은 호스팅이면 파일 대신 **Variables 화면**에 같은 값들을 넣습니다.)

봇은 "토큰을 특정 chat에 연결"하는 구조가 아닙니다. 토큰만 있으면 봇이 살아나고, **그 봇에게 말을 거는 누구에게나** 응답합니다. 그래서 아래처럼 **우리 팀만** 쓰도록 잠그는 걸 권장합니다.

## 🔒 우리 팀만 사용하게 잠그기 (chat ID 허용 목록)

API 비용이 들기 때문에, 허가된 사람만 쓰도록 제한할 수 있어요.

1. 봇을 실행한 뒤, 사용할 사람이 각자 봇에게 **`/id`** 를 보냅니다 → 자신의 **chat ID**(숫자)를 알려 줍니다.
2. 그 ID들을 `.env`에 콤마로 넣습니다:
   ```dotenv
   CMO_ALLOWED_CHAT_IDS=123456789,987654321
   ```
3. 봇을 재시작합니다. 이제 목록에 있는 사람만 사용할 수 있고, 나머지에게는 거절 메시지 + 본인 chat ID를 보여 줍니다.

> 비워 두면(`CMO_ALLOWED_CHAT_IDS` 미설정) **누구나** 사용 가능합니다. 운영 시에는 꼭 채우는 걸 권장해요.

## 🟢 상시 구동 (24시간 운영)

봇은 폴링 방식이라 **항상 켜져 있는 환경**에서 돌아야 합니다. 가장 쉬운 두 가지:

### A. Docker (권장 — 재부팅/크래시 시 자동 재시작)
서버(작은 클라우드 VM, 집/사무실의 상시 PC 등)에 Docker만 있으면 됩니다.
```bash
cp .env.example .env   # 토큰/키/허용목록 입력
docker compose up -d --build   # 백그라운드 상시 구동
docker compose logs -f         # 로그 보기
docker compose down            # 중지
```
`restart: unless-stopped` 설정 덕분에 서버를 재부팅해도 봇이 자동으로 다시 뜹니다.

### A-2. Railway (클라우드 — 현재 운영 방식)
1. [railway.com](https://railway.com) → New Project → **Deploy from GitHub repo** → 이 저장소 선택 (브랜치 `main`)
2. **Variables**에 `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, `CMO_ALLOWED_CHAT_IDS` 입력 (+ 선택: `NAVER_CLIENT_ID/SECRET`)
3. **(권장) 볼륨 연결** — 대화·노트가 재배포에도 유지되게:
   - 서비스 우클릭 → **Attach Volume** → Mount path `/data`
   - Variables에 `CMO_DATA_DIR=/data` 추가
   - 볼륨이 없어도 봇은 정상 동작하지만, 재배포 때 대화 기록·노트가 초기화됩니다.

### B. systemd (리눅스 서버에 직접)
`/etc/systemd/system/cmo-bot.service`:
```ini
[Unit]
Description=Sloboda CMO Telegram bot
After=network-online.target

[Service]
WorkingDirectory=/opt/sloboda-marketing
ExecStart=/opt/sloboda-marketing/.venv/bin/python run.py
EnvironmentFile=/opt/sloboda-marketing/.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cmo-bot
sudo journalctl -u cmo-bot -f   # 로그
```

> 노트북에서 `python run.py`로 띄워도 되지만, 노트북을 끄거나 잠자기에 들어가면 봇도 멈춥니다. 24시간 운영하려면 위 A 또는 B를 쓰세요. 대화 메모리는 메모리에 저장되어 재시작 시 초기화됩니다.

## 환경 변수 (`.env`)

| 변수 | 필수 | 기본값 | 설명 |
|------|:----:|--------|------|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | BotFather 토큰 |
| `CMO_PROVIDER` | | `gemini` | LLM 제공사: `gemini` 또는 `anthropic` |
| `GEMINI_API_KEY` | gemini일 때 ✅ | — | Google AI Studio 키 |
| `CMO_GEMINI_MODEL` | | `gemini-2.5-flash` | Gemini 모델. 더 저렴/무료티어: `gemini-2.5-flash-lite` |
| `ANTHROPIC_API_KEY` | anthropic일 때 ✅ | — | Anthropic API 키 |
| `CMO_MODEL` | | `claude-opus-4-8` | (anthropic) Claude 모델. 비용↓: `claude-sonnet-4-6`, `claude-haiku-4-5` |
| `CMO_ALLOWED_CHAT_IDS` | | (비어 있음) | 허용할 chat ID 목록(콤마). 비우면 전체 공개 |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | | (비어 있음) | 네이버 검색 API 키 — 있으면 `/naver` 활성화 ([무료 발급](https://developers.naver.com/apps/)) |
| `CMO_DATA_DIR` | | `data` | 대화·노트 영구 저장 경로 (Railway 볼륨 마운트 경로로 지정) |
| `CMO_BRIEFING_WEEKDAY` | | `1` | 주간 브리핑 요일 (0=일 … 6=토) |
| `CMO_BRIEFING_HOUR` | | `9` | 주간 브리핑 시각 (KST) |
| `CMO_MAX_TOKENS` | | `8000` | 답변 최대 토큰 |
| `CMO_ENABLE_WEB_SEARCH` | | `true` | 실시간 시장 조사(웹검색) 사용 |
| `CMO_ENABLE_THINKING` | | `true` | 추론 사용 (false면 비용↓) |
| `CMO_HISTORY_MAX_MESSAGES` | | `24` | 대화 메모리 길이 |
| `CMO_REQUEST_TIMEOUT` | | `300` | API 요청 타임아웃(초) |

## 구조

```
run.py                  # 진입점
cmo_bot/
  config.py             # 환경 변수 / 설정
  brand.py              # 브랜드 지식 + CMO 시스템 프롬프트 (지식의 단일 출처)
  menu.py               # 인라인 "마케팅 옵션" 메뉴
  llm.py                # 제공사 선택 (CMO_PROVIDER → gemini / anthropic)
  gemini_client.py      # Gemini 호출 (Google 검색 그라운딩 + 이미지 분석)
  claude_client.py      # Claude 호출 (adaptive thinking + web_search)
  naver.py              # 네이버 쇼핑/블로그 실데이터 조회 (/naver)
  bot.py                # 텔레그램 핸들러 / 영구 메모리 / 노트 / 브리핑 / 메시지 분할
requirements.txt
Dockerfile               # 컨테이너 이미지
docker-compose.yml       # 상시 구동(자동 재시작)
.env.example
```

## 동작 방식 (간단히)

`bot.py`가 텔레그램 메시지를 받아 채팅별 대화 기록에 쌓고, 워커 스레드에서
`llm.generate()`(→ `CMO_PROVIDER`에 따라 Gemini 또는 Claude)를 호출합니다.
모델은 `brand.py`의 CMO 시스템 프롬프트로 역할을 부여받고, 필요 시 실시간 웹검색으로
최신 시장 정보를 조사한 뒤 답합니다. 답변은 텔레그램 길이에 맞게 분할되어 전송됩니다.

## 비용 메모

- 기본 제공사는 **Gemini**로, Claude(Opus)보다 훨씬 저렴합니다.
  - 참고 단가: Gemini 2.5 Flash ≈ $0.30/$2.50, **Flash-Lite ≈ $0.10/$0.40 (무료 티어 있음)**, Claude Opus ≈ $5/$25 (입력/출력 1M 토큰).
- 더 아끼는 법 — `.env`에:
  ```dotenv
  CMO_GEMINI_MODEL=gemini-2.5-flash-lite   # 가장 저렴 (+ 무료 티어)
  CMO_ENABLE_WEB_SEARCH=false              # 실시간 조사 끄기 (큰 절감)
  CMO_ENABLE_THINKING=false                # 추론 끄기
  ```

## 운영 메모

- 봇은 폴링 방식으로 동작하므로 **항상 켜져 있는 환경**(개인 서버, 작은 VM, 라즈베리파이 등)에서
  `python run.py`로 띄워 두면 됩니다.
- 대화 기록·데이터 노트·브리핑 설정은 `CMO_DATA_DIR`(기본 `./data`)에 저장되어 재시작에도 유지됩니다.
  (Railway처럼 파일시스템이 초기화되는 환경에서는 볼륨을 연결해야 유지돼요.)
- 시크릿(`.env`)은 절대 깃에 커밋하지 마세요. (`.gitignore`에 이미 포함)

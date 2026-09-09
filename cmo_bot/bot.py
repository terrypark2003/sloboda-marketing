"""Telegram bot wiring for the Sloboda CMO."""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
from zoneinfo import ZoneInfo

from telegram import Chat, Update
from telegram.constants import ChatAction, ChatType
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from . import config, menu, naver
from .brand import HELP, WEEKLY_BRIEFING_PROMPT, WELCOME
from .llm import generate

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cmo_bot")

TELEGRAM_LIMIT = 3900  # safely under Telegram's 4096-char message cap
KST = ZoneInfo("Asia/Seoul")
MAX_NOTES = 30
NOTE_MAX_LEN = 500
WEEKDAY_LABELS = ["일", "월", "화", "수", "목", "금", "토"]  # 0=일 … 6=토 (PTB 규약)


def _authorized(update: Update) -> bool:
    """Open to all when no allowlist is set; otherwise restrict to allowed chats."""
    if not config.ALLOWED_CHAT_IDS:
        return True
    chat = update.effective_chat
    return bool(chat and chat.id in config.ALLOWED_CHAT_IDS)


async def _reject(message, chat_id: int) -> None:
    await message.reply_text(
        "🔒 이 봇은 허가된 사용자만 사용할 수 있어요.\n"
        f"당신의 chat ID: `{chat_id}`\n"
        "관리자에게 이 ID 등록을 요청하세요."
    )


def _trim_history(messages: list[dict]) -> list[dict]:
    """Keep memory bounded; always start on a user message."""
    msgs = list(messages)
    while len(msgs) > config.HISTORY_MAX_MESSAGES:
        msgs.pop(0)
    while msgs and msgs[0].get("role") != "user":
        msgs.pop(0)
    return msgs


def _notes_block(notes: list[str]) -> str | None:
    """Format team data notes for injection into the system prompt."""
    if not notes:
        return None
    return (
        "[팀이 기록한 데이터 노트 — 최신 실데이터로 간주하고 답변에 반영]\n"
        + "\n".join(f"- {n}" for n in notes)
    )


def _chunk(text: str) -> list[str]:
    """Split a long reply into Telegram-sized pieces on line boundaries."""
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        while len(line) > TELEGRAM_LIMIT:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:TELEGRAM_LIMIT])
            line = line[TELEGRAM_LIMIT:]
        if len(current) + len(line) + 1 > TELEGRAM_LIMIT:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks or [text]


async def _send_long(message, text: str) -> None:
    for piece in _chunk(text):
        await message.reply_text(piece)


async def _keep_typing(chat: Chat, coro):
    """Show a typing indicator until ``coro`` completes, then return its result."""
    task = asyncio.ensure_future(coro)
    while not task.done():
        try:
            await chat.send_action(ChatAction.TYPING)
        except Exception:  # noqa: BLE001 — typing is best-effort
            pass
        await asyncio.wait({task}, timeout=4)
    return task.result()


async def _ask_cmo(
    message,
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE,
    user_content: str,
    image: tuple[bytes, str] | None = None,
) -> None:
    history: list[dict] = context.chat_data.setdefault("history", [])
    history.append({"role": "user", "content": user_content})
    notes_ctx = _notes_block(context.chat_data.get("notes", []))
    try:
        text, new_history, stop = await _keep_typing(
            chat, asyncio.to_thread(generate, history, notes_ctx, image)
        )
    except Exception:  # noqa: BLE001
        logger.exception("CMO generation failed")
        if history and history[-1].get("role") == "user":
            history.pop()  # roll back so the next try isn't corrupted
        await message.reply_text(
            "⚠️ 처리 중 오류가 발생했어요. API 키 설정을 확인하거나 잠시 후 다시 시도해 주세요."
        )
        return

    context.chat_data["history"] = _trim_history(new_history)

    if stop == "refusal":
        await message.reply_text(
            "죄송해요, 그 요청은 도와드리기 어려워요. 마케팅 관련 질문으로 다시 물어봐 주세요."
        )
        return
    await _send_long(message, text or "음… 답변을 만들지 못했어요. 다시 한 번 시도해 주세요.")


def _addressed_to_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, str]:
    """In group chats, only respond when mentioned or replied to.

    Returns (should_respond, text_with_mention_stripped).
    """
    msg = update.message
    text = (msg.text or msg.caption or "").strip()
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return True, text
    username = context.bot.username
    mention = f"@{username}" if username else None
    if mention and mention in text:
        return True, text.replace(mention, "").strip()
    replied = msg.reply_to_message
    if replied and replied.from_user and replied.from_user.id == context.bot.id:
        return True, text
    return False, text


# --- handlers -------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data.setdefault("history", [])
    await update.message.reply_text(WELCOME, reply_markup=menu.keyboard())


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "무엇을 도와드릴까요? 아래에서 골라 주세요 👇", reply_markup=menu.keyboard()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP)


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["history"] = []
    await update.message.reply_text(
        "🧹 대화 맥락을 초기화했어요. (데이터 노트는 유지 — 목록: /notes)"
    )


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    status = "✅ 사용 허가됨" if _authorized(update) else "🔒 미등록(허용 목록에 없음)"
    await update.message.reply_text(f"이 채팅의 chat ID: `{chat.id}`\n상태: {status}")


async def cmd_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    text = " ".join(context.args).strip() if context.args else ""
    if not text:
        await update.message.reply_text(
            "사용법: /note 기록할 내용\n"
            "예) /note 지난주 스토어 방문 1,200명, 전환율 1.1%\n"
            "예) /note 와디즈 알림신청 240명 (6/21 기준)"
        )
        return
    notes: list[str] = context.chat_data.setdefault("notes", [])
    stamp = datetime.datetime.now(KST).strftime("%m/%d")
    notes.append(f"({stamp}) {text[:NOTE_MAX_LEN]}")
    while len(notes) > MAX_NOTES:
        notes.pop(0)
    await update.message.reply_text(
        f"📝 기록했어요. (총 {len(notes)}개)\n앞으로 모든 답변에 이 데이터를 참고할게요. 목록: /notes"
    )


async def cmd_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    notes: list[str] = context.chat_data.get("notes", [])
    if not notes:
        await update.message.reply_text(
            "아직 기록된 데이터 노트가 없어요.\n/note 내용 으로 기록해 보세요."
        )
        return
    lines = [f"{i}. {n}" for i, n in enumerate(notes, 1)]
    await _send_long(
        update.message,
        "📒 데이터 노트 (모든 답변에 반영됨)\n\n" + "\n".join(lines) + "\n\n삭제: /delnote 번호",
    )


async def cmd_delnote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    notes: list[str] = context.chat_data.get("notes", [])
    try:
        idx = int(context.args[0])
        removed = notes.pop(idx - 1)
    except (IndexError, ValueError, TypeError):
        await update.message.reply_text("사용법: /delnote 번호  (번호는 /notes 에서 확인)")
        return
    await update.message.reply_text(f"🗑 삭제했어요: {removed}")


async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    arg = context.args[0].lower() if context.args else ""
    chats: set[int] = context.bot_data.setdefault("briefing_chats", set())
    chat_id = update.effective_chat.id
    day = WEEKDAY_LABELS[config.BRIEFING_WEEKDAY % 7]
    if arg == "on":
        chats.add(chat_id)
        await update.message.reply_text(
            f"⏰ 주간 브리핑 켰어요. 매주 {day}요일 오전 {config.BRIEFING_HOUR}시(KST)에 "
            "시장 동향 + 이번 주 액션을 보내드릴게요.\n지금 바로 보기: /briefing now"
        )
    elif arg == "off":
        chats.discard(chat_id)
        await update.message.reply_text("⏹ 주간 브리핑을 껐어요. 다시 켜기: /briefing on")
    elif arg == "now":
        await update.message.reply_text("📅 브리핑 준비 중… 시장 조사를 포함해 1~2분 걸릴 수 있어요.")
        await _ask_cmo(update.message, update.effective_chat, context, WEEKLY_BRIEFING_PROMPT)
    else:
        status = "✅ 켜짐" if chat_id in chats else "⏹ 꺼짐"
        await update.message.reply_text(
            f"⏰ 주간 CMO 브리핑 — 현재 이 채팅: {status}\n"
            f"매주 {day}요일 오전 {config.BRIEFING_HOUR}시(KST) 발송\n\n"
            "/briefing on — 켜기\n/briefing off — 끄기\n/briefing now — 지금 바로 받기"
        )


async def cmd_naver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_text(
            "사용법: /naver 검색어\n예) /naver 민감성 재생크림\n"
            "네이버 쇼핑 실시간 경쟁 데이터를 조회해서 분석해 드려요."
        )
        return
    if not naver.available():
        await update.message.reply_text(
            "🔑 네이버 API 키가 아직 없어요. (무료, 5분 소요)\n"
            "1) https://developers.naver.com/apps/ 에서 애플리케이션 등록\n"
            "2) '검색' API 선택 → Client ID/Secret 발급\n"
            "3) 서버 환경변수에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 추가 후 재시작"
        )
        return
    await update.message.reply_text(f"🛒 네이버에서 '{query}' 실시간 데이터 조회 중…")
    try:
        snapshot = await asyncio.to_thread(naver.market_snapshot, query)
    except Exception:  # noqa: BLE001
        logger.exception("Naver lookup failed")
        await update.message.reply_text(
            "⚠️ 네이버 조회에 실패했어요. API 키가 올바른지, '검색' API 권한이 있는지 확인해 주세요."
        )
        return
    user_content = (
        f"{snapshot}\n\n"
        f"위 네이버 실시간 데이터를 근거로 '{query}' 시장을 분석해줘: "
        "경쟁 강도(등록 상품 수·상위 노출 브랜드), 가격대 대비 우리 포지션(43,000원), "
        "상품명에 넣을 키워드 제안, 그리고 노출을 늘리기 위한 다음 액션."
    )
    await _ask_cmo(update.message, update.effective_chat, context, user_content)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    if not _authorized(update):
        await _reject(update.message, update.effective_chat.id)
        return
    respond, text = _addressed_to_bot(update, context)
    if not respond or not text:
        return
    await _ask_cmo(update.message, update.effective_chat, context, text)


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.photo:
        return
    if not _authorized(update):
        await _reject(msg, update.effective_chat.id)
        return
    if update.effective_chat.type != ChatType.PRIVATE:
        respond, _ = _addressed_to_bot(update, context)
        if not respond:
            return
    if config.PROVIDER != "gemini":
        await msg.reply_text("이미지 분석은 Gemini 제공사(CMO_PROVIDER=gemini)에서 지원돼요.")
        return
    try:
        file = await msg.photo[-1].get_file()
        data = bytes(await file.download_as_bytearray())
    except Exception:  # noqa: BLE001
        logger.exception("photo download failed")
        await msg.reply_text("⚠️ 이미지를 받지 못했어요. 다시 보내 주세요.")
        return
    caption = (msg.caption or "").strip()
    question = caption or (
        "이 이미지를 슬로보다 마케팅 관점에서 분석해줘. "
        "상세페이지/광고 시안이면 개선점을, 경쟁사 화면이면 벤치마킹 포인트를 알려줘."
    )
    await _ask_cmo(
        msg,
        update.effective_chat,
        context,
        f"[이미지 첨부] {question}",
        image=(data, "image/jpeg"),
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _authorized(update):
        await _reject(query.message, update.effective_chat.id)
        return
    prompt = menu.preset(query.data)
    if not prompt:
        return
    label = menu.label(query.data) or "옵션"
    await query.message.reply_text(f"➡️ {label} 진행할게요.")
    await _ask_cmo(query.message, query.message.chat, context, prompt)


async def weekly_briefing_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Proactive Monday-morning briefing for opted-in chats."""
    app = context.application
    chat_ids = set(app.bot_data.get("briefing_chats", set()))
    if not chat_ids:
        return
    logger.info("weekly briefing → %d chat(s)", len(chat_ids))
    for chat_id in chat_ids:
        try:
            chat_data = app.chat_data[chat_id]
            notes_ctx = _notes_block(chat_data.get("notes", []))
            fresh = [{"role": "user", "content": WEEKLY_BRIEFING_PROMPT}]
            text, new_history, _ = await asyncio.to_thread(generate, fresh, notes_ctx)
            if not text:
                continue
            for piece in _chunk("📅 주간 CMO 브리핑\n\n" + text):
                await context.bot.send_message(chat_id, piece)
            # Keep the briefing in that chat's memory so follow-ups have context.
            chat_data["history"] = _trim_history(
                list(chat_data.get("history", [])) + new_history
            )
        except Exception:  # noqa: BLE001
            logger.exception("weekly briefing failed for chat %s", chat_id)
    try:
        app.mark_data_for_update_persistence(chat_ids=chat_ids)
    except Exception:  # noqa: BLE001
        pass


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error", exc_info=context.error)


def main() -> None:
    config.validate()
    os.makedirs(config.DATA_DIR, exist_ok=True)
    persistence = PicklePersistence(
        filepath=os.path.join(config.DATA_DIR, "cmo_state.pkl")
    )
    app = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("notes", cmd_notes))
    app.add_handler(CommandHandler("delnote", cmd_delnote))
    app.add_handler(CommandHandler("briefing", cmd_briefing))
    app.add_handler(CommandHandler("naver", cmd_naver))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)

    if app.job_queue:
        app.job_queue.run_daily(
            weekly_briefing_job,
            time=datetime.time(hour=config.BRIEFING_HOUR, tzinfo=KST),
            days=(config.BRIEFING_WEEKDAY % 7,),
            name="weekly_briefing",
        )
    else:  # pragma: no cover — job-queue extra not installed
        logger.warning(
            "JobQueue unavailable — weekly briefing disabled "
            "(pip install 'python-telegram-bot[job-queue]')"
        )

    access = (
        f"{len(config.ALLOWED_CHAT_IDS)}개 chat 허용"
        if config.ALLOWED_CHAT_IDS
        else "전체 공개(allowlist 미설정)"
    )
    logger.info(
        "Sloboda CMO bot starting (provider=%s, model=%s, access=%s, naver=%s, data=%s)…",
        config.PROVIDER,
        config.active_model(),
        access,
        "on" if naver.available() else "off",
        config.DATA_DIR,
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

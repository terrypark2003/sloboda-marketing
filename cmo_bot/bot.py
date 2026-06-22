"""Telegram bot wiring for the Sloboda CMO."""

from __future__ import annotations

import asyncio
import logging

from telegram import Chat, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import config, menu
from .brand import HELP, WELCOME
from .claude_client import generate

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cmo_bot")

TELEGRAM_LIMIT = 3900  # safely under Telegram's 4096-char message cap


def _trim_history(messages: list[dict]) -> list[dict]:
    """Keep memory bounded; always start on a user message."""
    msgs = list(messages)
    while len(msgs) > config.HISTORY_MAX_MESSAGES:
        msgs.pop(0)
    while msgs and msgs[0].get("role") != "user":
        msgs.pop(0)
    return msgs


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


async def _ask_cmo(message, chat: Chat, context: ContextTypes.DEFAULT_TYPE, user_content: str) -> None:
    history: list[dict] = context.chat_data.setdefault("history", [])
    history.append({"role": "user", "content": user_content})
    try:
        text, new_history, stop = await _keep_typing(
            chat, asyncio.to_thread(generate, history)
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
    await update.message.reply_text("🧹 대화 맥락을 초기화했어요. 새 주제로 시작해 볼까요?")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    await _ask_cmo(update.message, update.effective_chat, context, update.message.text)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    prompt = menu.preset(query.data)
    if not prompt:
        return
    label = menu.label(query.data) or "옵션"
    await query.message.reply_text(f"➡️ {label} 진행할게요.")
    await _ask_cmo(query.message, query.message.chat, context, prompt)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error", exc_info=context.error)


def main() -> None:
    config.validate()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)

    logger.info("Sloboda CMO bot starting (model=%s)…", config.MODEL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

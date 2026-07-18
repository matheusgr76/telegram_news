"""
news_handler.py
Handles the /news Telegram command.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

import config
from services.news_fetcher import fetch_all_news
from services.briefing_builder import build_briefing
from formatters.telegram_formatter import split_message

logger = logging.getLogger(__name__)


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch articles, build briefing, send to user. Owner-only."""
    if str(update.effective_chat.id) != str(config.TELEGRAM_CHAT_ID):
        logger.warning("Rejected /news from unauthorized chat_id=%s", update.effective_chat.id)
        return

    await update.message.reply_text("⏳ Fetching your briefing, one moment...")

    try:
        sections = await fetch_all_news()
        briefing = await build_briefing(sections)
        chunks = split_message(briefing)
        for chunk in chunks:
            await update.message.reply_text(chunk)
    except Exception as exc:
        logger.error("Error in /news handler: %s", exc)
        await update.message.reply_text("⚠️ Something went wrong building the briefing. Check the logs.")

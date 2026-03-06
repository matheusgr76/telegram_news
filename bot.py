"""
bot.py
Entry point for the News Feed Telegram bot.
- Registers /news command handler
- Schedules daily briefing at SCHEDULE_HOUR:SCHEDULE_MINUTE (SCHEDULE_TZ)
- Runs polling loop
"""
import asyncio
import datetime
import logging

import pytz
from telegram.ext import Application, CommandHandler

import config
from handlers.news_handler import news_command
from services.news_fetcher import fetch_all_news
from services.briefing_builder import build_briefing
from formatters.telegram_formatter import split_message

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


async def _send_scheduled_briefing(context) -> None:
    """Job callback: build and push the daily briefing."""
    logger.info("Scheduled briefing triggered.")
    try:
        sections = await fetch_all_news()
        briefing = await build_briefing(sections)
        chunks = split_message(briefing)
        for chunk in chunks:
            await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=chunk)
        logger.info("Scheduled briefing sent successfully.")
    except Exception as exc:
        logger.error("Scheduled briefing failed: %s", exc)
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=f"⚠️ Scheduled briefing failed: {exc}",
        )


def _schedule_daily(app: Application) -> None:
    tz = pytz.timezone(config.SCHEDULE_TZ)
    target_time = datetime.time(
        hour=config.SCHEDULE_HOUR,
        minute=config.SCHEDULE_MINUTE,
        tzinfo=tz,
    )
    app.job_queue.run_daily(_send_scheduled_briefing, time=target_time)
    logger.info(
        "Daily briefing scheduled at %02d:%02d %s",
        config.SCHEDULE_HOUR,
        config.SCHEDULE_MINUTE,
        config.SCHEDULE_TZ,
    )


def main() -> None:
    # Python 3.12+ no longer creates an event loop implicitly.
    # Set one explicitly so python-telegram-bot's internal get_event_loop() succeeds.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("news", news_command))
    _schedule_daily(app)
    logger.info("News Feed bot started. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

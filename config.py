import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val

# Telegram
TELEGRAM_TOKEN: str = _require("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID: str = _require("TELEGRAM_CHAT_ID")

# News APIs
NEWSAPI_KEY: str = _require("NEWSAPI_KEY")
THENEWSAPI_KEY: str = _require("THENEWSAPI_KEY")

# LLM
GEMINI_API_KEY: str = _require("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Schedule (defaults to 08:30 America/Sao_Paulo)
SCHEDULE_HOUR: int = int(os.getenv("SCHEDULE_HOUR", "8"))
SCHEDULE_MINUTE: int = int(os.getenv("SCHEDULE_MINUTE", "30"))
SCHEDULE_TZ: str = os.getenv("SCHEDULE_TZ", "America/Sao_Paulo")

# HTTP timeouts
HTTP_TIMEOUT_SECONDS: int = int(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))

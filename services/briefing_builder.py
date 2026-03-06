"""
briefing_builder.py
Sends fetched articles to Gemini 1.5 Flash and returns the
formatted daily briefing as a string.
"""
import datetime
import logging

import google.generativeai as genai
import pytz

import config
from services.news_fetcher import Article

logger = logging.getLogger(__name__)

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel(config.GEMINI_MODEL)

_BRIEFING_PROMPT = """\
You are a sharp, opinionated news editor writing a daily briefing for a sophisticated reader.

Today's date (Brasília time): {date}

Below are raw news articles grouped by section. Using ONLY this information, write a briefing in EXACTLY this format — no deviations:

Here's your {date_long} briefing:

🔥 BIGGEST STORY: [WRITE A PUNCHY TITLE IN CAPS]
* [key development] [Source Name]
* [key development] [Source Name]
* [key development] [Source Name]

💰 MARKETS
* [key development] [Source Name]
* [key development] [Source Name]

⚖️ US DOMESTIC
* [key development] [Source Name]
* [key development] [Source Name]

📱 TECH/BUSINESS
* [key development] [Source Name]
* [key development] [Source Name]

TL;DR: [2-3 sharp, opinionated sentences connecting the day's biggest themes. Use your voice — be direct, add editorial weight, connect dots. No fluff.]

Rules:
- Use ONLY facts from the articles below. Do NOT hallucinate.
- Source name = the publication, not the URL.
- Each bullet = one tight sentence max.
- The TL;DR must be analytical and opinionated, not a summary bullet list.
- Output nothing else — no preamble, no sign-off.

--- ARTICLES ---
{articles}
"""


def _format_articles(sections: dict[str, list[Article]]) -> str:
    section_labels = {
        "biggest_story": "BIGGEST STORY",
        "markets": "MARKETS",
        "us_domestic": "US DOMESTIC",
        "tech_business": "TECH/BUSINESS",
    }
    lines: list[str] = []
    for key, label in section_labels.items():
        articles = sections.get(key, [])
        lines.append(f"[{label}]")
        if not articles:
            lines.append("  (no articles fetched)")
        for a in articles:
            lines.append(f"  - {a['title']} | {a['source']} | {a['description']}")
        lines.append("")
    return "\n".join(lines)


def _today_strings() -> tuple[str, str]:
    tz = pytz.timezone(config.SCHEDULE_TZ)
    now = datetime.datetime.now(tz)
    date_short = now.strftime("%Y-%m-%d")
    month = now.strftime("%B")
    date_long = f"{month} {now.day}, {now.year}"
    return date_short, date_long


async def build_briefing(sections: dict[str, list[Article]]) -> str:
    date_short, date_long = _today_strings()
    article_text = _format_articles(sections)
    prompt = _BRIEFING_PROMPT.format(
        date=date_short,
        date_long=date_long,
        articles=article_text,
    )
    try:
        response = await _model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return f"⚠️ Could not generate briefing: {exc}"

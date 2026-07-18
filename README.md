# News Feed — Telegram Bot

A Telegram bot that delivers a daily news briefing in an opinionated, section-based format.

## Features
- `/news` command — fetch briefing on demand (owner-only — replies are restricted to the chat ID in `TELEGRAM_CHAT_ID`)
- Auto-push daily at **08:30 Brasília time** (GMT-3)
- Sources: NewsAPI.org + The News API (both free tiers)
- Summarised by Groq (Llama 3.3) into 5 fixed sections

## Setup

### 1. Create the bot
1. Open Telegram → search `@BotFather`
2. Send `/newbot`
3. Name: **News Feed** | Username: pick something unique (e.g. `plym_newsfeed_bot`)
4. Copy the token

### 2. Get your Chat ID
1. Start a chat with your bot (send `/start`)
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat": {"id": ...}` — that's your `TELEGRAM_CHAT_ID`

### 3. Get API keys
- **NewsAPI.org**: https://newsapi.org/register (free)
- **The News API**: https://www.thenewsapi.com/ (free tier)
- **Groq**: https://console.groq.com (free)

### 4. Configure environment
```bash
cp .env.example .env
# Fill in all values in .env
```

### 5. Install dependencies
```bash
pip install -r requirements.txt
```

### 6. Run
```bash
python bot.py
```

The bot will start polling and the daily schedule will be active.

## Project Structure
```
Telegram_news/
├── bot.py                          # Entry point
├── config.py                       # Env var loader
├── handlers/
│   └── news_handler.py             # /news command
├── services/
│   ├── news_fetcher.py             # Dual-API news fetcher
│   └── briefing_builder.py         # Groq LLM briefing generator
├── formatters/
│   └── telegram_formatter.py       # Message chunker
├── .env.example                    # Key template
└── requirements.txt
```

## License

MIT — see [`LICENSE`](LICENSE).

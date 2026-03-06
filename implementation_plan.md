# News Feed — Telegram Bot — Implementation Plan (SWITCHING TO GROQ)

## Architecture (Updated)

| Decision | Choice |
|---|---|
| News APIs | NewsAPI.org + The News API (free tiers) |
| LLM | Groq (Llama-3.3-70b-versatile) |
| Sections | Fixed: Biggest Story · Markets · US Domestic · Tech/Business · TL;DR |
| Schedule | 08:30 daily, `America/Sao_Paulo` (GMT-3) |
| Deployment | Local process |
| Bot name | **News Feed** |

## Files Created ✓

| File | Purpose |
|---|---|
| `bot.py` | Entry point, polling, JobQueue scheduler |
| `config.py` | Env var loader — fails fast on missing keys |
| `handlers/news_handler.py` | `/news` command |
| `services/news_fetcher.py` | Dual-API fetcher, normalised schema |
| `services/briefing_builder.py` | Groq prompt → formatted briefing (NEEDS UPDATE) |
| `formatters/telegram_formatter.py` | Message chunker (4000-char limit) |
| `.env.example` | Key template |
| `.gitignore` | Excludes `.env` and pycache |
| `README.md` | Setup + run guide |

## API Usage Budget

| API | Free Limit | Per Briefing | Margin |
|---|---|---|---|
| NewsAPI.org | 100 req/day | 4 calls | 96% remaining |
| The News API | 100 req/day | 4 calls | 96% remaining |
| Groq | Free tier (varies) | 1 call | High (llama-3-70b) |

## Verification (Phase 5)

1. Create bot → BotFather → paste token into `.env`
2. Get Chat ID → paste into `.env`
3. Collect API keys (NewsAPI, TheNewsAPI, Groq) → paste into `.env`
4. `pip install -r requirements.txt`
5. `python bot.py`
6. Send `/news` → briefing arrives, all 5 sections, today's date

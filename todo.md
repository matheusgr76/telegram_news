# News Feed Bot — Task Checklist

## Session 2 Status

### ✅ Done
- Project scaffold (config, .env, requirements, gitignore, README)
- `services/news_fetcher.py` — dual-API fetcher (NewsAPI.org + TheNewsAPI)
- `services/briefing_builder.py` — Initial Gemini logic (Deprecated in favor of Groq)
- `formatters/telegram_formatter.py` — chunker
- `handlers/news_handler.py` — /news command
- `bot.py` — polling + APScheduler 08:30 GMT-3
- Fixed: Python 3.14 asyncio event loop issue
- Fixed: Windows strftime %-d crash
- 8 smoke tests passing

### 🔄 In Progress — Switching to Groq
- [ ] Install `groq` SDK
- [ ] Update `config.py` with `GROQ_API_KEY`
- [ ] Update `.env.example`
- [ ] Refactor `services/briefing_builder.py` for Groq
- [ ] Update `smoke_test.py` for Groq e2e verification

## Phase 5: Verification — NEXT
- [ ] Resolve LLM provider (Switched to Groq)
- [ ] Send /news → full briefing received with all 5 sections
- [ ] Confirm date in header matches today
- [ ] Wait for or simulate 08:30 scheduled push

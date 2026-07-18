"""
smoke_test.py
Verification suite for the News Feed bot critical path.
Includes one live API call (Groq) to catch auth/model issues before ship.
Run: python smoke_test.py
"""
import sys
import datetime
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Force UTF-8 stdout so the → / • / emoji in test output don't crash on
# Windows' default cp1252 console.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── 1. date formatting (the bug we just fixed) ─────────────────────────────

def test_today_strings_windows_safe():
    """strftime with %-d must never be called on Windows."""
    # Import with live config patched so no .env needed
    with patch.dict("os.environ", {
        "TELEGRAM_TOKEN": "x", "TELEGRAM_CHAT_ID": "1",
        "NEWSAPI_KEY": "x", "THENEWSAPI_KEY": "x",
        "GROQ_API_KEY": "x",
    }):
        # Force reload config to pick up patches if needed, 
        # but here we just need the function behavior
        from services.briefing_builder import _today_strings
        date_short, date_long = _today_strings()

    # Note: _today_strings in Groq version now uses now.day logic
    assert "-" in date_short, f"Bad format: {date_short}"
    assert "," in date_long, f"date_long missing comma: {date_long}"
    # e.g. "March 5, 2026"
    parts = date_long.split(" ")
    assert len(parts) == 3, f"date_long wrong parts: {date_long}"
    print(f"  [PASS] date strings: short={date_short}  long={date_long}")


# ── 2. telegram formatter — chunking ───────────────────────────────────────

def test_formatter_short_message():
    from formatters.telegram_formatter import split_message
    text = "Hello world"
    chunks = split_message(text)
    assert chunks == ["Hello world"], f"Unexpected: {chunks}"
    print(f"  [PASS] short message → 1 chunk")


def test_formatter_long_message():
    from formatters.telegram_formatter import split_message
    line = "A" * 100 + "\n"
    text = line * 50           # 5050 chars — over 4000 limit
    chunks = split_message(text)
    assert len(chunks) > 1, "Long message should split"
    for chunk in chunks:
        assert len(chunk) <= 4000, f"Chunk too large: {len(chunk)}"
    # Reassembled text must equal original
    assert "".join(chunks) == text, "Chunks don't reassemble correctly"
    print(f"  [PASS] long message ({len(text)} chars) → {len(chunks)} chunks, all ≤ 4000")


def test_formatter_empty():
    from formatters.telegram_formatter import split_message
    chunks = split_message("")
    assert chunks == [""], f"Empty string should give ['']"
    print(f"  [PASS] empty string → ['']")


# ── 3. news_fetcher normalisation ──────────────────────────────────────────

def test_newsapi_normaliser():
    with patch.dict("os.environ", {
        "TELEGRAM_TOKEN": "x", "TELEGRAM_CHAT_ID": "1",
        "NEWSAPI_KEY": "x", "THENEWSAPI_KEY": "x", "GROQ_API_KEY": "x",
    }):
        from services.news_fetcher import _from_newsapi
    raw = {"title": "Big news", "description": "Details", "url": "http://x.com",
           "source": {"name": "Reuters"}}
    article = _from_newsapi(raw, "markets")
    assert article["title"] == "Big news"
    assert article["source"] == "Reuters"
    assert article["section"] == "markets"
    print(f"  [PASS] NewsAPI normaliser")


def test_thenewsapi_normaliser():
    with patch.dict("os.environ", {
        "TELEGRAM_TOKEN": "x", "TELEGRAM_CHAT_ID": "1",
        "NEWSAPI_KEY": "x", "THENEWSAPI_KEY": "x", "GROQ_API_KEY": "x",
    }):
        from services.news_fetcher import _from_thenewsapi
    raw = {"title": "Market rally", "description": "Stocks up", "url": "http://y.com",
           "source": "Bloomberg"}
    article = _from_thenewsapi(raw, "markets")
    assert article["title"] == "Market rally"
    assert article["source"] == "Bloomberg"
    assert article["section"] == "markets"
    print(f"  [PASS] TheNewsAPI normaliser")


# ── 4. config — fails fast on missing keys ─────────────────────────────────

def test_config_loads_successfully():
    """All required keys must be present and non-empty after loading .env."""
    import sys
    for mod in list(sys.modules):
        if mod == "config":
            del sys.modules[mod]
    import config
    required = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID",
                "NEWSAPI_KEY", "THENEWSAPI_KEY", "GROQ_API_KEY"]
    for key in required:
        val = getattr(config, key, None)
        assert val, f"config.{key} is empty or missing"
    print(f"  [PASS] config loads all {len(required)} required keys")

# ── 5. Groq connectivity (live — catches wrong model names) ──────────────

def test_groq_connectivity():
    """Verify configured model is reachable with the real API key."""
    import config
    from groq import Groq
    client = Groq(api_key=config.GROQ_API_KEY)
    
    # Try a simple sync completion call as a "ping"
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "ping"}],
            model=config.GROQ_MODEL,
            max_tokens=10,
        )
        assert completion.choices[0].message.content, "Empty response from Groq"
        print(f"  [PASS] Groq model '{config.GROQ_MODEL}' is reachable and responding")
    except Exception as e:
        # Check if it's a 404 or 401 specifically
        raise RuntimeError(f"Groq connectivity failed: {e}")


TESTS = [
    test_today_strings_windows_safe,
    test_formatter_short_message,
    test_formatter_long_message,
    test_formatter_empty,
    test_newsapi_normaliser,
    test_thenewsapi_normaliser,
    test_config_loads_successfully,
    test_groq_connectivity,
]

if __name__ == "__main__":
    print(f"\nRunning {len(TESTS)} smoke tests...\n")
    passed, failed = 0, 0
    for test in TESTS:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)

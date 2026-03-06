"""
telegram_formatter.py
Splits long briefings into Telegram-safe chunks (<= 4000 chars).
No HTML/Markdown escaping — briefing uses plain text with Unicode emoji.
"""

MAX_CHUNK = 4000


def split_message(text: str) -> list[str]:
    """
    Split text into chunks that fit Telegram's 4096-char message limit.
    Splits on newlines where possible to avoid cutting mid-sentence.
    """
    if len(text) <= MAX_CHUNK:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in text.splitlines(keepends=True):
        if current_len + len(line) > MAX_CHUNK:
            if current:
                chunks.append("".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line)

    if current:
        chunks.append("".join(current))

    return chunks

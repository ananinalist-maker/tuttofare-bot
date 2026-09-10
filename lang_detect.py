"""Определение языка клиента.

Порядок сигналов — от самого надёжного к самому слабому:
1. Текст, который клиент написал сам (кириллица / итальянские / английские маркеры).
2. Язык интерфейса Telegram (language_code) — приходит даже с голой командой /start.
3. Итальянский по умолчанию: основной рынок — Рим и Витербо.
"""

import re

from locales import DEFAULT_LANG, LANGS

CYRILLIC = re.compile(r"[а-яёіїєґ]", re.IGNORECASE)
WORD = re.compile(r"[a-zàèéìòùA-ZÀÈÉÌÒÙ']+")

# Частотные слова, которые почти не пересекаются между языками.
IT_MARKERS = {
    "ciao", "buongiorno", "buonasera", "salve", "vorrei", "avrei", "bisogno",
    "ristrutturare", "ristrutturazione", "bagno", "casa", "appartamento",
    "preventivo", "quanto", "costa", "costo", "prezzo", "piastrelle", "posa",
    "grazie", "sono", "mi", "vorremmo", "fare", "lavori", "cantiere", "mq",
    "per", "una", "che", "non", "come", "dove", "quando", "anche", "della",
}
EN_MARKERS = {
    "hello", "hi", "hey", "good", "morning", "evening", "need", "want", "would",
    "like", "how", "much", "cost", "price", "quote", "bathroom", "renovation",
    "renovate", "flat", "apartment", "tiles", "tiling", "thanks", "thank",
    "please", "your", "the", "and", "what", "where", "when", "can", "you",
}


def detect(text: str | None, telegram_lang_code: str | None) -> str:
    """Возвращает код языка из LANGS."""
    text = (text or "").strip()

    if text:
        # Кириллица — однозначный сигнал, дальше можно не смотреть.
        letters = [c for c in text if c.isalpha()]
        if letters:
            cyr = sum(1 for c in letters if CYRILLIC.match(c))
            if cyr / len(letters) > 0.3:
                return "ru"

        words = {w.lower() for w in WORD.findall(text)}
        it_hits = len(words & IT_MARKERS)
        en_hits = len(words & EN_MARKERS)
        if it_hits or en_hits:
            return "it" if it_hits >= en_hits else "en"

    code = (telegram_lang_code or "").lower()
    if code:
        prefix = code.split("-")[0]
        if prefix in LANGS:
            return prefix
        # Украинский и белорусский интерфейс — русскоязычная диаспора.
        if prefix in ("uk", "be", "kk"):
            return "ru"

    return DEFAULT_LANG

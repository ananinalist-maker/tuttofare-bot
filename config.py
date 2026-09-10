"""Конфигурация бота: читает переменные окружения, валидирует обязательные."""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Куда слать заявки. Можно несколько id через запятую.
ADMIN_CHAT_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_CHAT_ID", "").split(",")
    if x.strip().lstrip("-").isdigit()
]

DB_PATH = os.getenv("DB_PATH", "leads.db").strip() or "leads.db"

# Куда ведём клиента после заявки — реальный контакт мастера.
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "+39 389 448 1853").strip()
SITE_URL = os.getenv("SITE_URL", "https://tuttofare-roma.vercel.app").strip()


def validate() -> None:
    """Падаем сразу и с понятной ошибкой, а не через час молчания на сервере."""
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN не задан.\n"
            "Локально: скопируй .env.example в .env и впиши токен от @BotFather.\n"
            "На Railway: Variables -> BOT_TOKEN."
        )
    if not ADMIN_CHAT_IDS:
        print(
            "[warn] ADMIN_CHAT_ID не задан — заявки будут сохраняться в базу, "
            "но уведомления в Telegram не придут. Напиши боту /id, чтобы узнать свой id."
        )

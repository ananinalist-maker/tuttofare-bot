"""Tuttofare-Roma — Telegram-бот квалификации заявок на ремонт.

Ведёт клиента по 7 вопросам на его языке (IT / RU / EN), считает приоритет лида
и присылает мастеру карточку с готовым решением: ехать на замер сегодня, завтра
или не ехать вовсе.

Запуск: python bot.py
"""

import html
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
import lang_detect
import qualify
import storage
from locales import LANG_NAMES, LANGS, t

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s — %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("tuttofare-bot")

# Состояния диалога
(START_SCREEN, SERVICE, SEGMENT, GEO, AREA, TIMING, BUDGET, NAME, CONTACT) = range(9)


# --------------------------------------------------------------------- утилиты


def lang_of(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "it")


def kb(lang: str, prefix: str, keys: list[str], per_row: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура из вариантов ответа: callback_data = 'prefix:key'."""
    buttons = [
        InlineKeyboardButton(t(lang, f"{prefix}_{k}"), callback_data=f"{prefix}:{k}")
        for k in keys
    ]
    rows = [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]
    return InlineKeyboardMarkup(rows)


def start_screen_kb(lang: str) -> InlineKeyboardMarkup:
    lang_row = [
        InlineKeyboardButton(
            ("• " if code == lang else "") + LANG_NAMES[code], callback_data=f"lang:{code}"
        )
        for code in LANGS
    ]
    go = {"it": "▶️ Iniziamo", "ru": "▶️ Начать", "en": "▶️ Start"}[lang]
    return InlineKeyboardMarkup([lang_row, [InlineKeyboardButton(go, callback_data="go")]])


async def ask(query, lang: str, text_key: str, prefix: str, keys: list[str], per_row: int = 1):
    await query.edit_message_text(
        t(lang, text_key), reply_markup=kb(lang, prefix, keys, per_row),
        parse_mode=ParseMode.HTML,
    )


# ------------------------------------------------------------------- сценарий


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    lang = lang_detect.detect(update.message.text if update.message else None,
                              user.language_code if user else None)
    context.user_data.clear()
    context.user_data["lang"] = lang

    await update.message.reply_text(
        f"{t(lang, 'greeting')}\n\n{t(lang, 'lang_hint')}",
        reply_markup=start_screen_kb(lang),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    return START_SCREEN


async def on_start_screen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("lang:"):
        lang = query.data.split(":", 1)[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            f"{t(lang, 'greeting')}\n\n{t(lang, 'lang_hint')}",
            reply_markup=start_screen_kb(lang),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return START_SCREEN

    lang = lang_of(context)
    await ask(query, lang, "ask_service", "service", qualify.SERVICES)
    return SERVICE


async def on_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = query.data.split(":", 1)[1]
    lang = lang_of(context)
    await ask(query, lang, "ask_segment", "segment", qualify.SEGMENTS)
    return SEGMENT


async def on_segment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["segment"] = query.data.split(":", 1)[1]
    lang = lang_of(context)
    await ask(query, lang, "ask_geo", "geo", qualify.GEOS)
    return GEO


async def on_geo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    geo = query.data.split(":", 1)[1]
    context.user_data["geo"] = geo
    lang = lang_of(context)

    # Вне Рима и Витербо диалог дальше не идёт: незачем собирать контакт,
    # по которому мы всё равно не поедем.
    if geo == "fuori":
        await query.edit_message_text(
            t(lang, "out_of_area", site=config.SITE_URL),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        await finish(update, context, verdict=qualify.evaluate(dict(context.user_data)))
        return ConversationHandler.END

    await query.edit_message_text(t(lang, "ask_area"), parse_mode=ParseMode.HTML)
    return AREA


async def on_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    raw = (update.message.text or "").strip().replace(",", ".")
    digits = "".join(c for c in raw if c.isdigit() or c == ".")

    try:
        value = float(digits)
        if not 1 <= value <= 5000:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(lang, "invalid_area"), parse_mode=ParseMode.HTML)
        return AREA

    context.user_data["area"] = f"{value:g} м²"
    await update.message.reply_text(
        t(lang, "ask_timing"),
        reply_markup=kb(lang, "timing", qualify.TIMINGS),
        parse_mode=ParseMode.HTML,
    )
    return TIMING


async def on_timing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["timing"] = query.data.split(":", 1)[1]
    lang = lang_of(context)
    await ask(query, lang, "ask_budget", "budget", qualify.BUDGETS, per_row=2)
    return BUDGET


async def on_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["budget"] = query.data.split(":", 1)[1]
    lang = lang_of(context)
    await query.edit_message_text(t(lang, "ask_name"), parse_mode=ParseMode.HTML)
    return NAME


async def on_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data["name"] = (update.message.text or "").strip()[:100]

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(t(lang, "btn_share_contact"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        t(lang, "ask_contact"), reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    return CONTACT


async def on_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    message = update.message

    if message.contact:
        contact = message.contact.phone_number
    else:
        contact = (message.text or "").strip()
        # Достаточно проверить, что в строке есть похожее на номер количество цифр.
        if sum(c.isdigit() for c in contact) < 7:
            await message.reply_text(t(lang, "invalid_contact"), parse_mode=ParseMode.HTML)
            return CONTACT

    context.user_data["contact"] = contact[:100]
    verdict = qualify.evaluate(dict(context.user_data))
    lead_id = await finish(update, context, verdict)

    await message.reply_text(
        t(lang, "done", n=lead_id, phone=config.WHATSAPP_PHONE),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# ------------------------------------------------ сохранение и карточка мастеру


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE,
                 verdict: qualify.Verdict) -> int:
    user = update.effective_user
    data = context.user_data

    lead_id = storage.save_lead({
        "tg_user_id": user.id,
        "tg_username": user.username,
        "lang": data.get("lang"),
        "service": data.get("service"),
        "segment": data.get("segment"),
        "geo": data.get("geo"),
        "area": data.get("area"),
        "timing": data.get("timing"),
        "budget": data.get("budget"),
        "name": data.get("name"),
        "contact": data.get("contact"),
        "score": verdict.score,
        "status": verdict.status,
    })

    await notify_admins(context, lead_id, data, verdict, user)
    context.user_data.clear()
    return lead_id


def lead_card(lead_id: int, data: dict, verdict: qualify.Verdict, user) -> str:
    """Карточка для мастера — всегда по-русски, независимо от языка клиента."""

    def ru(prefix: str, key: str | None) -> str:
        return t("ru", f"{prefix}_{key}") if key else "—"

    def esc(value) -> str:
        return html.escape(str(value)) if value else "—"

    username = f" (@{user.username})" if user.username else ""
    lang_name = {"it": "итальянский", "ru": "русский", "en": "английский"}.get(
        data.get("lang", ""), data.get("lang", "—")
    )

    lines = [
        f"<b>{verdict.label} — {verdict.score}/{qualify.MAX_SCORE}</b>",
        f"Заявка №{lead_id}",
        "",
        f"👤 {esc(data.get('name'))}{html.escape(username)}",
        f"📞 <code>{esc(data.get('contact'))}</code>",
        f"🌐 Язык клиента: {lang_name}",
        "",
        f"🔧 {ru('service', data.get('service'))}",
        f"🎯 {ru('segment', data.get('segment'))}",
        f"📍 {ru('geo', data.get('geo'))}",
        f"📐 {esc(data.get('area'))}",
        f"⏱ {ru('timing', data.get('timing'))}",
        f"💰 {ru('budget', data.get('budget'))}",
    ]

    warnings = {
        "price_anchor": (
            "⚠️ Бюджет ниже рыночного пола для этих работ — ожидания сформированы "
            "рекламой агрегаторов («от 299 €/м²»). Проговорить вилку до выезда."
        ),
        "just_looking": "ℹ️ Клиент пока только собирает информацию — это догрев, не сделка.",
        "b2b": "⭐️ B2B-контакт: один архитектор — это 5–7 проектов в год.",
    }
    flag_lines = [warnings[f] for f in verdict.flags if f in warnings]
    if flag_lines:
        lines += ["", *flag_lines]

    playbook = qualify.SEGMENT_PLAYBOOK.get(data.get("segment", ""))
    if playbook:
        lines += ["", f"🧠 {playbook}"]

    lines += ["", f"➡️ <b>{verdict.next_step}</b>"]
    return "\n".join(lines)


async def notify_admins(context: ContextTypes.DEFAULT_TYPE, lead_id: int, data: dict,
                        verdict: qualify.Verdict, user) -> None:
    if not config.ADMIN_CHAT_IDS:
        log.warning("Заявка №%s сохранена, но ADMIN_CHAT_ID не задан — уведомление не ушло.",
                    lead_id)
        return

    card = lead_card(lead_id, data, verdict, user)
    for chat_id in config.ADMIN_CHAT_IDS:
        try:
            await context.bot.send_message(chat_id, card, parse_mode=ParseMode.HTML)
        except Forbidden:
            log.error("Мастер с id %s не начал диалог с ботом — уведомление не доставлено.",
                      chat_id)
        except TelegramError:
            log.exception("Не удалось отправить заявку №%s в чат %s", lead_id, chat_id)


# -------------------------------------------------------------------- команды


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = lang_of(context)
    context.user_data.clear()
    await update.message.reply_text(
        t(lang, "cancel"), reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = lang_detect.detect(update.message.text, update.effective_user.language_code)
    await update.message.reply_text(
        t(context.user_data.get("lang", lang), "help",
          phone=config.WHATSAPP_PHONE, site=config.SITE_URL),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = lang_of(context)
    rows = [[InlineKeyboardButton(LANG_NAMES[c], callback_data=f"setlang:{c}")] for c in LANGS]
    await update.message.reply_text(
        t(lang, "lang_hint"), reply_markup=InlineKeyboardMarkup(rows)
    )


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":", 1)[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(t(lang, "lang_switched"))


async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Помогает узнать свой chat id при настройке ADMIN_CHAT_ID."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Твой chat id: <code>{chat_id}</code>\n\n"
        f"Впиши его в переменную <code>ADMIN_CHAT_ID</code>, чтобы получать заявки сюда.",
        parse_mode=ParseMode.HTML,
    )


def _admin_only(update: Update) -> bool:
    return update.effective_user.id in config.ADMIN_CHAT_IDS


async def leads_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _admin_only(update):
        return
    rows = storage.recent_leads(10)
    if not rows:
        await update.message.reply_text("Заявок пока нет.")
        return

    icon = {"hot": "🔥", "warm": "🌤", "cold": "❄️", "out_of_area": "⛔️"}
    lines = ["<b>Последние заявки</b>", ""]
    for r in rows:
        when = r["created_at"][:16].replace("T", " ")
        service = t("ru", "service_" + r["service"]) if r["service"] else "—"
        geo = t("ru", "geo_" + r["geo"]) if r["geo"] else "—"
        lines.append(
            f"{icon.get(r['status'], '•')} <b>№{r['id']}</b> · {when} · "
            f"{r['score']}/{qualify.MAX_SCORE}\n"
            f"   {html.escape(r['name'] or '—')} · <code>{html.escape(r['contact'] or '—')}</code>\n"
            f"   {service} · {geo}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _admin_only(update):
        return
    s = storage.stats()
    await update.message.reply_text(
        "<b>Статистика</b>\n\n"
        f"Всего заявок: {s.get('total', 0)}\n"
        f"🔥 Горячих: {s.get('hot', 0)}\n"
        f"🌤 Тёплых: {s.get('warm', 0)}\n"
        f"❄️ Холодных: {s.get('cold', 0)}\n"
        f"⛔️ Вне зоны: {s.get('out_of_area', 0)}",
        parse_mode=ParseMode.HTML,
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Ошибка при обработке апдейта", exc_info=context.error)


async def post_init(app: Application) -> None:
    from telegram import BotCommand

    await app.bot.set_my_commands([
        BotCommand("start", "Nuova richiesta / Новая заявка / New request"),
        BotCommand("lang", "Cambia lingua / Сменить язык / Change language"),
        BotCommand("cancel", "Annulla / Отменить / Cancel"),
        BotCommand("help", "Info"),
    ])
    me = await app.bot.get_me()
    log.info("Бот запущен: @%s", me.username)


def main() -> None:
    config.validate()
    storage.init_db()

    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_SCREEN: [CallbackQueryHandler(on_start_screen, pattern=r"^(lang:|go$)")],
            SERVICE: [CallbackQueryHandler(on_service, pattern=r"^service:")],
            SEGMENT: [CallbackQueryHandler(on_segment, pattern=r"^segment:")],
            GEO: [CallbackQueryHandler(on_geo, pattern=r"^geo:")],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_area)],
            TIMING: [CallbackQueryHandler(on_timing, pattern=r"^timing:")],
            BUDGET: [CallbackQueryHandler(on_budget, pattern=r"^budget:")],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_name)],
            CONTACT: [
                MessageHandler(filters.CONTACT, on_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_contact),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        allow_reentry=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("leads", leads_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(set_lang, pattern=r"^setlang:"))
    app.add_error_handler(on_error)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

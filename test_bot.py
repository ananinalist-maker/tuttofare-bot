"""Локальные тесты без обращения к Telegram.

Запуск: python test_bot.py
Токен не нужен — проверяется вся логика, которая не зависит от сети:
определение языка, скоринг лида, полнота переводов, база, карточка мастеру.
"""

import os
import sys
import tempfile
from types import SimpleNamespace

# Подменяем базу на временную ДО импорта модулей, которые читают конфиг.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DB_PATH"] = _tmp.name
os.environ.setdefault("BOT_TOKEN", "test:token")

import lang_detect  # noqa: E402
import locales as L  # noqa: E402
import qualify as q  # noqa: E402
import storage  # noqa: E402
from bot import lead_card  # noqa: E402

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  ok   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}" + (f" — {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{title}")


# ------------------------------------------------------------- определение языка
section("Определение языка клиента")

check("кириллица → ru", lang_detect.detect("Здравствуйте, нужен ремонт ванной", "it") == "ru")
check("итальянский текст → it", lang_detect.detect("Buongiorno, vorrei ristrutturare il bagno", "en") == "it")
check("английский текст → en", lang_detect.detect("Hello, I need a bathroom renovation quote", "it") == "en")
check("пустой текст → язык интерфейса", lang_detect.detect("", "ru") == "ru")
check("украинский интерфейс → ru", lang_detect.detect("", "uk") == "ru")
check("регион в коде языка (it-IT) → it", lang_detect.detect("", "it-IT") == "it")
check("ничего неизвестно → итальянский по умолчанию", lang_detect.detect("", "zh") == "it")
check("голое /start с ru-интерфейсом → ru", lang_detect.detect("/start", "ru") == "ru")

# ------------------------------------------------------------------- переводы
section("Полнота переводов")

base_keys = set(L.TEXTS["it"])
for lang in L.LANGS:
    check(f"{lang}: набор ключей совпадает с итальянским",
          set(L.TEXTS[lang]) == base_keys,
          str(set(L.TEXTS[lang]) ^ base_keys))

for prefix, keys in [("service", q.SERVICES), ("segment", q.SEGMENTS), ("geo", q.GEOS),
                     ("timing", q.TIMINGS), ("budget", q.BUDGETS)]:
    missing = [f"{lang}/{prefix}_{k}" for lang in L.LANGS for k in keys
               if f"{prefix}_{k}" not in L.TEXTS[lang]]
    check(f"подписи для всех вариантов «{prefix}»", not missing, str(missing))

check("подстановка переменных работает", "№7" in L.t("ru", "done", n=7, phone="+39"))
check("неизвестный язык не роняет бота", L.t("de", "cancel") == L.TEXTS["it"]["cancel"])

# --------------------------------------------------------------------- скоринг
section("Квалификация лида")

hot = q.evaluate({"service": "bagno", "segment": "casa", "geo": "roma_nord",
                  "timing": "subito", "budget": "15_40"})
check("идеальный лид = горячий и максимум баллов",
      hot.status == "hot" and hot.score == q.MAX_SCORE, f"{hot.status} {hot.score}")

out = q.evaluate({"service": "bagno", "segment": "casa", "geo": "fuori",
                  "timing": "subito", "budget": "gt80"})
check("другой регион = вне зоны, несмотря на бюджет", out.status == "out_of_area")
check("вне зоны не назначаем выезд", "не назначаем" in out.next_step)

anchor = q.evaluate({"service": "bagno", "segment": "investimento", "geo": "roma_prov",
                     "timing": "3_6", "budget": "lt5"})
check("бюджет до 5 000 € на ванную помечен ценовым якорем", "price_anchor" in anchor.flags)
check("такой лид не горячий", anchor.status == "cold", anchor.status)

small = q.evaluate({"service": "altro", "segment": "casa", "geo": "roma_nord",
                    "timing": "subito", "budget": "lt5"})
check("мелкая работа за малый бюджет якорем НЕ помечается", "price_anchor" not in small.flags)

b2b = q.evaluate({"service": "completa", "segment": "professionista", "geo": "viterbo",
                  "timing": "1_3", "budget": "40_80"})
check("архитектор помечен как B2B", "b2b" in b2b.flags)
check("архитектор с реальным бюджетом = горячий", b2b.status == "hot", b2b.status)

looking = q.evaluate({"service": "piastrelle", "segment": "casa", "geo": "roma_altro",
                      "timing": "informazione", "budget": "non_so"})
check("«просто узнаю» помечено как догрев", "just_looking" in looking.flags)

check("у каждого статуса есть подпись и следующий шаг",
      all(q.Verdict(0, s).label and q.Verdict(0, s).next_step
          for s in ("hot", "warm", "cold", "out_of_area")))

check("баллы никогда не превышают максимум",
      all(q.evaluate({"service": s, "segment": sg, "geo": g, "timing": tm, "budget": b}).score
          <= q.MAX_SCORE
          for s in q.SERVICES for sg in q.SEGMENTS for g in q.GEOS
          for tm in q.TIMINGS for b in q.BUDGETS))

# ----------------------------------------------------------------------- база
section("Сохранение заявок")

storage.init_db()
lead = {"tg_user_id": 42, "tg_username": "anna", "lang": "ru", "service": "bagno",
        "segment": "casa", "geo": "roma_nord", "area": "8 м²", "timing": "subito",
        "budget": "15_40", "name": "Анна", "contact": "+39 333 1234567",
        "score": 15, "status": "hot"}
lead_id = storage.save_lead(lead)
check("заявка получает номер", isinstance(lead_id, int) and lead_id > 0)

rows = storage.recent_leads(5)
check("заявка читается обратно", rows and rows[0]["name"] == "Анна")
check("контакт сохранён без искажений", rows[0]["contact"] == "+39 333 1234567")
check("статистика считает заявку", storage.stats()["total"] >= 1)

second = storage.save_lead({**lead, "name": "Marco", "status": "cold", "score": 6})
check("номера заявок растут", second > lead_id)
check("статистика разделяет статусы", storage.stats().get("cold", 0) >= 1)

# ------------------------------------------------------------ карточка мастеру
section("Карточка для мастера")

user = SimpleNamespace(id=42, username="anna", language_code="ru")
card = lead_card(1, {**lead, "lang": "ru"}, hot, user)
check("в карточке есть статус", "ГОРЯЧИЙ" in card)
check("в карточке есть контакт", "+39 333 1234567" in card)
check("в карточке есть следующий шаг", "сопралуого" in card)
check("подсказка по сегменту подставлена", "Перфекционист" in card)
check("данные переведены на русский для мастера", "Ванная под ключ" in card)

anchor_card = lead_card(2, {**lead, "budget": "lt5", "segment": "investimento"}, anchor, user)
check("предупреждение о ценовом якоре видно мастеру", "299" in anchor_card)
check("подсказка по инвестору подставлена", "DiCo" in anchor_card)

inject_user = SimpleNamespace(id=1, username=None, language_code="it")
inject_card = lead_card(3, {**lead, "name": "<b>хакер</b>", "contact": "<script>"}, hot,
                        inject_user)
check("HTML из ответов клиента экранируется",
      "&lt;b&gt;хакер&lt;/b&gt;" in inject_card and "<script>" not in inject_card)

card_it = lead_card(4, {**lead, "lang": "it"}, hot, user)
check("карточка мастеру всегда по-русски, даже для клиента-итальянца",
      "Ванная под ключ" in card_it and "итальянский" in card_it)

# ----------------------------------------------------------------------- итог
os.unlink(_tmp.name)
print(f"\n{'=' * 46}")
print(f"Пройдено: {passed}   Провалено: {failed}")
print("=" * 46)
sys.exit(1 if failed else 0)

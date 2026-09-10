"""Логика квалификации лида.

Зачем это вообще нужно. По стратегии Tuttofare-Roma смета бесплатная, но готовится
только после реального выезда на объект (сопралуого). Значит каждый нецелевой лид —
это потерянные полдня мастера. Плюс агрегаторы приучили рынок к «ремонту от 299 €/м²»,
а премиальный сегмент стартует от ~1 000 €/м² — с холодного трафика это даёт большой
процент отказов уже на этапе сметы.

Поэтому бот считает лид ДО выезда: гео, тип работ, сегмент, срок и бюджет.
Мастер видит приоритет заявки и не тратит день на клиента, который искал «за 299».
"""

from dataclasses import dataclass, field

# --- Варианты ответов. Ключи неизменны, подписи живут в locales.py ---------------

SERVICES = ["bagno", "piastrelle", "completa", "altro"]
SEGMENTS = ["casa", "investimento", "professionista"]
GEOS = ["roma_nord", "roma_altro", "roma_prov", "viterbo", "viterbo_prov", "fuori"]
TIMINGS = ["subito", "1_3", "3_6", "informazione"]
BUDGETS = ["lt5", "5_15", "15_40", "40_80", "gt80", "non_so"]

# --- Веса --------------------------------------------------------------------
# Гео: приоритет — Север Рима и Витербо (высокий чек / слабые конкуренты онлайн).
GEO_SCORE = {
    "roma_nord": 3,
    "viterbo": 3,
    "roma_altro": 2,
    "viterbo_prov": 2,
    "roma_prov": 1,
    "fuori": 0,
}

# Ниша входа — сложные санузлы и крупноформатная плитка.
SERVICE_SCORE = {"bagno": 3, "piastrelle": 3, "completa": 2, "altro": 1}

# Архитектор = самый прибыльный сегмент: 1 партнёр даёт 5–7 проектов в год.
SEGMENT_SCORE = {"professionista": 3, "casa": 3, "investimento": 2}

TIMING_SCORE = {"subito": 3, "1_3": 2, "3_6": 1, "informazione": 0}

# Ориентиры рынка Лацио 2026: ванная «под ключ» 5–12 тыс. €, дизайнерская 15–20 тыс. €,
# полная реновация 70–90 м² — 70–120 тыс. €.
BUDGET_SCORE = {"lt5": -2, "5_15": 2, "15_40": 3, "40_80": 3, "gt80": 3, "non_so": 1}

# Работы, для которых бюджет до 5 000 € заведомо ниже рыночного пола.
BUDGET_SENSITIVE_SERVICES = {"bagno", "piastrelle", "completa"}

MAX_SCORE = 15

# Что говорить мастеру перед звонком: главное возражение сегмента и чем крыть.
SEGMENT_PLAYBOOK = {
    "casa": (
        "Перфекционист. Возражение: «почему укладка так дорого». "
        "Крыть крупным форматом, заусовкой 45°, UNI 11493. "
        "Скрытый страх — аванс и конфликт с соседями: показать A Corpo и «Buon Vicinato»."
    ),
    "investimento": (
        "Инвестор. Возражение: «другой посчитал вдвое дешевле», может просить «вчёрную». "
        "Крыть DiCo и легальностью: без неё нет вычета и нельзя продать квартиру. "
        "Считать в деньгах простоя, а не в €/м²."
    ),
    "professionista": (
        "B2B, самый прибыльный сегмент. Возражение: недоверие к новой фирме, "
        "страх что уведём клиента. Крыть чтением чертежей, чек-листом «12 проверок» "
        "и письменным Change Order."
    ),
}


@dataclass
class Verdict:
    score: int
    status: str  # hot | warm | cold | out_of_area
    flags: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return {
            "hot": "🔥 ГОРЯЧИЙ",
            "warm": "🌤 ТЁПЛЫЙ",
            "cold": "❄️ ХОЛОДНЫЙ",
            "out_of_area": "⛔️ ВНЕ ЗОНЫ",
        }[self.status]

    @property
    def next_step(self) -> str:
        return {
            "hot": "Связаться сегодня. Назначить сопралуого, смета за 48 ч.",
            "warm": "Связаться в течение суток. Уточнить объём до выезда.",
            "cold": "Догрев контентом. Выезд только после уточнения бюджета и сроков.",
            "out_of_area": "Вне географии — выезд не назначаем.",
        }[self.status]


def evaluate(answers: dict[str, str]) -> Verdict:
    """Считает лид по ответам. Ключи: service, segment, geo, timing, budget."""
    geo = answers.get("geo", "")
    service = answers.get("service", "")
    budget = answers.get("budget", "")

    # Вне Рима и Витербо не работаем — выезд физически не окупается.
    if geo == "fuori":
        return Verdict(score=0, status="out_of_area", flags=["out_of_area"])

    score = (
        GEO_SCORE.get(geo, 0)
        + SERVICE_SCORE.get(service, 0)
        + SEGMENT_SCORE.get(answers.get("segment", ""), 0)
        + TIMING_SCORE.get(answers.get("timing", ""), 0)
        + BUDGET_SCORE.get(budget, 0)
    )

    flags: list[str] = []
    if budget == "lt5" and service in BUDGET_SENSITIVE_SERVICES:
        # Тот самый «prezzo d'attacco»: ожидания сформированы рекламой агрегаторов.
        flags.append("price_anchor")
    if answers.get("timing") == "informazione":
        flags.append("just_looking")
    if answers.get("segment") == "professionista":
        flags.append("b2b")

    if score >= 12:
        status = "hot"
    elif score >= 8:
        status = "warm"
    else:
        status = "cold"

    return Verdict(score=score, status=status, flags=flags)

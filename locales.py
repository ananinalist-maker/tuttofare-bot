"""Тексты бота на трёх языках: итальянский, русский, английский.

Разметка — HTML (а не Markdown), потому что в ответах клиента легко встречаются
символы вроде _ и *, на которых Markdown-парсер Telegram падает.
"""

LANGS = ("it", "ru", "en")
DEFAULT_LANG = "it"

LANG_NAMES = {"it": "🇮🇹 Italiano", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

TEXTS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ ITALIANO
    "it": {
        "greeting": (
            "👋 Benvenuto in <b>Tuttofare-Roma</b> — ristrutturazioni a Roma e Viterbo.\n\n"
            "Sono l'assistente di Florin, artigiano con 23 anni di esperienza.\n\n"
            "In 2 minuti raccolgo i dati del tuo progetto: così il sopralluogo è mirato e "
            "il <b>preventivo arriva entro 48 ore, gratis e senza impegno</b>.\n\n"
            "Nessun prezzo al m² inventato al telefono — prima vediamo il cantiere, poi il numero."
        ),
        "lang_hint": "Se preferisci un'altra lingua, scegli qui sotto 👇",
        "lang_switched": "Perfetto, continuiamo in italiano.",
        "ask_service": "<b>1/7.</b> Di cosa hai bisogno?",
        "ask_segment": "<b>2/7.</b> L'immobile a che scopo?",
        "ask_geo": "<b>3/7.</b> Dove si trova l'immobile?",
        "ask_area": (
            "<b>4/7.</b> Quanti metri quadri?\n\n"
            "Scrivi solo il numero. Se è un bagno, i m² del bagno.\n"
            "<i>Esempio: 8 oppure 75</i>"
        ),
        "ask_timing": "<b>5/7.</b> Quando vorresti iniziare?",
        "ask_budget": (
            "<b>6/7.</b> Che budget hai in mente?\n\n"
            "Serve per non far perdere tempo a nessuno. Riferimenti reali del mercato Lazio 2026: "
            "bagno chiavi in mano <b>5.000–12.000 €</b>, bagno di design <b>15.000–20.000 €</b>, "
            "ristrutturazione completa 70–90 m² <b>70.000–120.000 €</b>."
        ),
        "ask_name": "<b>7/7.</b> Come ti chiami?",
        "ask_contact": (
            "Ultimo passo: un recapito per richiamarti — telefono o WhatsApp.\n\n"
            "Puoi anche usare il pulsante qui sotto."
        ),
        "btn_share_contact": "📱 Condividi il mio numero",
        "invalid_area": "Scrivi solo il numero dei m², per favore. Esempio: 8",
        "invalid_contact": (
            "Mi serve un recapito valido: numero di telefono o WhatsApp.\n"
            "Esempio: +39 333 1234567"
        ),
        "done": (
            "✅ <b>Richiesta n. {n} registrata.</b>\n\n"
            "<b>Cosa succede adesso</b>\n"
            "1. Ti ricontattiamo entro la giornata lavorativa\n"
            "2. Fissiamo il sopralluogo sul posto\n"
            "3. Preventivo entro 48 ore dal sopralluogo — gratis, senza impegno\n\n"
            "<b>Come lavoriamo</b>\n"
            "• <b>Contratto A Corpo</b> — prezzo fisso per l'opera. Ogni variazione solo per "
            "iscritto: il preventivo non lievita\n"
            "• <b>Video Diario Cantiere</b> — video su WhatsApp 3 volte a settimana, segui i "
            "lavori senza venire in cantiere\n"
            "• <b>Tutti i documenti</b> — fattura, DiCo, Patente a Crediti. Senza questi non hai "
            "detrazioni e non vendi casa\n\n"
            "Urgente? WhatsApp: {phone}"
        ),
        "out_of_area": (
            "Grazie per il tempo! 🙏\n\n"
            "Lavoriamo solo su <b>Roma e Viterbo</b> con le rispettive province: più lontano non "
            "riusciamo a garantire il livello di controllo che promettiamo. Preferiamo dirtelo "
            "subito invece di farti perdere tempo.\n\n"
            "Se in futuro hai un immobile nella nostra zona, siamo qui: {site}"
        ),
        "cancel": "Va bene, ho annullato tutto. Per ricominciare: /start",
        "help": (
            "<b>Tuttofare-Roma — assistente richieste</b>\n\n"
            "/start — nuova richiesta\n"
            "/lang — cambia lingua\n"
            "/cancel — annulla la richiesta in corso\n\n"
            "Ristrutturazioni a Roma e Viterbo. WhatsApp: {phone}\n{site}"
        ),
        "already_running": "Stiamo già compilando una richiesta. Per ricominciare: /cancel",
        # варианты ответов
        "service_bagno": "🚿 Bagno chiavi in mano",
        "service_piastrelle": "🧱 Posa piastrelle grande formato",
        "service_completa": "🏠 Ristrutturazione completa",
        "service_altro": "✍️ Altro",
        "segment_casa": "🏡 Ci abiterò io",
        "segment_investimento": "📈 Affitto o rivendita",
        "segment_professionista": "📐 Sono architetto / designer",
        "geo_roma_nord": "Roma nord (Parioli, Flaminio, Trieste, Cassia)",
        "geo_roma_altro": "Roma, altra zona",
        "geo_roma_prov": "Provincia di Roma",
        "geo_viterbo": "Viterbo città",
        "geo_viterbo_prov": "Provincia di Viterbo",
        "geo_fuori": "Un'altra regione",
        "timing_subito": "⚡️ Entro un mese",
        "timing_1_3": "📅 Tra 1 e 3 mesi",
        "timing_3_6": "🗓 Tra 3 e 6 mesi",
        "timing_informazione": "🔍 Mi sto solo informando",
        "budget_lt5": "fino a 5.000 €",
        "budget_5_15": "5.000 – 15.000 €",
        "budget_15_40": "15.000 – 40.000 €",
        "budget_40_80": "40.000 – 80.000 €",
        "budget_gt80": "oltre 80.000 €",
        "budget_non_so": "Non lo so ancora",
    },
    # ------------------------------------------------------------------- РУССКИЙ
    "ru": {
        "greeting": (
            "👋 Добро пожаловать в <b>Tuttofare-Roma</b> — ремонт и реновация в Риме и Витербо.\n\n"
            "Я ассистент Флорина, мастера-отделочника с 23 годами практики.\n\n"
            "За 2 минуты соберу данные по объекту: тогда выезд будет предметным, а "
            "<b>смета придёт за 48 часов — бесплатно и без обязательств</b>.\n\n"
            "Никаких «цен за м²» по телефону — сначала смотрим объект, потом называем цифру."
        ),
        "lang_hint": "Если удобнее другой язык — выберите ниже 👇",
        "lang_switched": "Отлично, продолжаем на русском.",
        "ask_service": "<b>1/7.</b> Что нужно сделать?",
        "ask_segment": "<b>2/7.</b> Для чего объект?",
        "ask_geo": "<b>3/7.</b> Где находится объект?",
        "ask_area": (
            "<b>4/7.</b> Какая площадь в м²?\n\n"
            "Напишите числом. Если это ванная — площадь ванной.\n"
            "<i>Например: 8 или 75</i>"
        ),
        "ask_timing": "<b>5/7.</b> Когда планируете начать?",
        "ask_budget": (
            "<b>6/7.</b> На какой бюджет ориентируетесь?\n\n"
            "Спрашиваю, чтобы не тратить ваше и наше время на несовпадение ожиданий. "
            "Реальные ориентиры рынка Лацио 2026: ванная под ключ <b>5 000–12 000 €</b>, "
            "дизайнерская ванная <b>15 000–20 000 €</b>, полная реновация 70–90 м² "
            "<b>70 000–120 000 €</b>."
        ),
        "ask_name": "<b>7/7.</b> Как к вам обращаться?",
        "ask_contact": (
            "Последний шаг: контакт для связи — телефон или WhatsApp.\n\n"
            "Можно нажать кнопку ниже."
        ),
        "btn_share_contact": "📱 Отправить мой номер",
        "invalid_area": "Напишите, пожалуйста, только число — площадь в м². Например: 8",
        "invalid_contact": (
            "Нужен рабочий контакт: номер телефона или WhatsApp.\n"
            "Например: +39 333 1234567"
        ),
        "done": (
            "✅ <b>Заявка №{n} принята.</b>\n\n"
            "<b>Что дальше</b>\n"
            "1. Свяжемся с вами в течение рабочего дня\n"
            "2. Договоримся о выезде на объект\n"
            "3. Смета за 48 часов после выезда — бесплатно, без обязательств\n\n"
            "<b>Как мы работаем</b>\n"
            "• <b>Контракт A Corpo</b> — фиксированная цена за объём целиком. Любое изменение "
            "только письменно: смета не раздувается по ходу\n"
            "• <b>Video Diario Cantiere</b> — видеоотчёт в WhatsApp 3 раза в неделю, вы видите "
            "стройку не приезжая на объект\n"
            "• <b>Все документы</b> — fattura, DiCo, Patente a Crediti. Без них не будет "
            "налогового вычета и не продать квартиру\n\n"
            "Срочно? WhatsApp: {phone}"
        ),
        "out_of_area": (
            "Спасибо за время! 🙏\n\n"
            "Мы работаем только по <b>Риму и Витербо</b> с провинциями — дальше не сможем "
            "обеспечить тот контроль качества, который обещаем. Честнее сказать сразу, "
            "чем тянуть время.\n\n"
            "Если появится объект в нашей зоне — будем рады: {site}"
        ),
        "cancel": "Хорошо, отменил. Чтобы начать заново — /start",
        "help": (
            "<b>Tuttofare-Roma — ассистент по заявкам</b>\n\n"
            "/start — новая заявка\n"
            "/lang — сменить язык\n"
            "/cancel — отменить текущую заявку\n\n"
            "Ремонт и реновация в Риме и Витербо. WhatsApp: {phone}\n{site}"
        ),
        "already_running": "Мы уже заполняем заявку. Чтобы начать заново — /cancel",
        "service_bagno": "🚿 Ванная под ключ",
        "service_piastrelle": "🧱 Плитка крупного формата",
        "service_completa": "🏠 Полная реновация",
        "service_altro": "✍️ Другое",
        "segment_casa": "🏡 Для себя, буду жить",
        "segment_investimento": "📈 Под аренду или перепродажу",
        "segment_professionista": "📐 Я архитектор / дизайнер",
        "geo_roma_nord": "Рим, север (Parioli, Flaminio, Trieste, Cassia)",
        "geo_roma_altro": "Рим, другой район",
        "geo_roma_prov": "Провинция Рима",
        "geo_viterbo": "Витербо, город",
        "geo_viterbo_prov": "Провинция Витербо",
        "geo_fuori": "Другой регион",
        "timing_subito": "⚡️ В течение месяца",
        "timing_1_3": "📅 Через 1–3 месяца",
        "timing_3_6": "🗓 Через 3–6 месяцев",
        "timing_informazione": "🔍 Пока просто узнаю",
        "budget_lt5": "до 5 000 €",
        "budget_5_15": "5 000 – 15 000 €",
        "budget_15_40": "15 000 – 40 000 €",
        "budget_40_80": "40 000 – 80 000 €",
        "budget_gt80": "больше 80 000 €",
        "budget_non_so": "Пока не знаю",
    },
    # ------------------------------------------------------------------- ENGLISH
    "en": {
        "greeting": (
            "👋 Welcome to <b>Tuttofare-Roma</b> — renovation in Rome and Viterbo.\n\n"
            "I'm the assistant of Florin, a finishing craftsman with 23 years of practice.\n\n"
            "In 2 minutes I'll collect the details of your project, so the site visit is focused "
            "and the <b>quote arrives within 48 hours — free, no obligation</b>.\n\n"
            "No made-up price per m² over the phone — first we see the site, then we give a number."
        ),
        "lang_hint": "Prefer another language? Pick one below 👇",
        "lang_switched": "Great, let's continue in English.",
        "ask_service": "<b>1/7.</b> What do you need?",
        "ask_segment": "<b>2/7.</b> What is the property for?",
        "ask_geo": "<b>3/7.</b> Where is the property?",
        "ask_area": (
            "<b>4/7.</b> How many square metres?\n\n"
            "Just the number, please. If it's a bathroom — the bathroom's m².\n"
            "<i>For example: 8 or 75</i>"
        ),
        "ask_timing": "<b>5/7.</b> When would you like to start?",
        "ask_budget": (
            "<b>6/7.</b> What budget do you have in mind?\n\n"
            "I ask so neither of us wastes time on mismatched expectations. Real Lazio 2026 "
            "benchmarks: turnkey bathroom <b>€5,000–12,000</b>, designer bathroom "
            "<b>€15,000–20,000</b>, full renovation of 70–90 m² <b>€70,000–120,000</b>."
        ),
        "ask_name": "<b>7/7.</b> What's your name?",
        "ask_contact": (
            "Last step: a contact to reach you — phone or WhatsApp.\n\n"
            "You can also use the button below."
        ),
        "btn_share_contact": "📱 Share my number",
        "invalid_area": "Please send just the number of square metres. For example: 8",
        "invalid_contact": (
            "I need a working contact: a phone or WhatsApp number.\n"
            "For example: +39 333 1234567"
        ),
        "done": (
            "✅ <b>Request #{n} received.</b>\n\n"
            "<b>What happens next</b>\n"
            "1. We get back to you within the business day\n"
            "2. We arrange a site visit\n"
            "3. Quote within 48 hours of the visit — free, no obligation\n\n"
            "<b>How we work</b>\n"
            "• <b>A Corpo contract</b> — fixed price for the whole job. Any change only in "
            "writing, so the quote doesn't creep up\n"
            "• <b>Video Diario Cantiere</b> — video updates on WhatsApp 3 times a week, you "
            "follow the work without visiting\n"
            "• <b>Full paperwork</b> — invoice, DiCo, Patente a Crediti. Without these there's "
            "no tax deduction and no selling the flat\n\n"
            "Urgent? WhatsApp: {phone}"
        ),
        "out_of_area": (
            "Thank you for your time! 🙏\n\n"
            "We only work in <b>Rome and Viterbo</b> and their provinces — further out we can't "
            "guarantee the level of control we promise. Better to say so now than waste your time.\n\n"
            "If you ever have a property in our area, we're here: {site}"
        ),
        "cancel": "All right, cancelled. To start over: /start",
        "help": (
            "<b>Tuttofare-Roma — request assistant</b>\n\n"
            "/start — new request\n"
            "/lang — change language\n"
            "/cancel — cancel the current request\n\n"
            "Renovation in Rome and Viterbo. WhatsApp: {phone}\n{site}"
        ),
        "already_running": "We're already filling in a request. To start over: /cancel",
        "service_bagno": "🚿 Turnkey bathroom",
        "service_piastrelle": "🧱 Large-format tiling",
        "service_completa": "🏠 Full renovation",
        "service_altro": "✍️ Something else",
        "segment_casa": "🏡 For myself, I'll live there",
        "segment_investimento": "📈 To rent out or resell",
        "segment_professionista": "📐 I'm an architect / designer",
        "geo_roma_nord": "Rome north (Parioli, Flaminio, Trieste, Cassia)",
        "geo_roma_altro": "Rome, another area",
        "geo_roma_prov": "Province of Rome",
        "geo_viterbo": "Viterbo city",
        "geo_viterbo_prov": "Province of Viterbo",
        "geo_fuori": "Another region",
        "timing_subito": "⚡️ Within a month",
        "timing_1_3": "📅 In 1–3 months",
        "timing_3_6": "🗓 In 3–6 months",
        "timing_informazione": "🔍 Just gathering information",
        "budget_lt5": "up to €5,000",
        "budget_5_15": "€5,000 – 15,000",
        "budget_15_40": "€15,000 – 40,000",
        "budget_40_80": "€40,000 – 80,000",
        "budget_gt80": "over €80,000",
        "budget_non_so": "Don't know yet",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Достаёт текст. Если ключа нет в языке — падаем на итальянский, а не на KeyError."""
    bundle = TEXTS.get(lang) or TEXTS[DEFAULT_LANG]
    text = bundle.get(key) or TEXTS[DEFAULT_LANG].get(key, key)
    return text.format(**kwargs) if kwargs else text

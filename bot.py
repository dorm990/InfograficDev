import os, json, time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = os.getenv("8400519045:AAGJXXV8pHqsELUJ9APQqlSmWl2eJglDIEY")                 # новый токен
ADMIN_ID = int(os.getenv("7236376615", "0"))     # 7236376615
WEBAPP_URL = os.getenv("https://dorm990.github.io/InfograficDev/", "")       # ссылка GitHub Pages на мини-ап

bot = telebot.TeleBot(TOKEN)

ASSET_WELCOME = "assets/welcome_banner_v2.png"
ASSET_MENU = "assets/services_menu_v2.png"
LEADS_FILE = "leads.json"

SERVICES = [
    "Карточки WB/Ozon",
    "Сайт / лендинг",
    "Telegram-бот",
    "Mini App",
    "Моб. приложение",
    "Другое"
]

PRICING = {
    "Карточки WB/Ozon": [
        ("Start", "1 главный слайд (первый экран) + стиль", "быстрый старт / тест гипотезы"),
        ("Pro", "комплект 5–7 слайдов + инфографика", "полная упаковка товара"),
        ("Max", "7–10 слайдов + баннеры/вариации", "под линейку/акции"),
    ],
    "Сайт / лендинг": [
        ("Start", "одностраничник / витрина", "быстро показать оффер"),
        ("Pro", "много блоков + формы + адаптив", "под рекламу и заявки"),
        ("Max", "каталог/сложнее логика", "под магазин/сервис"),
    ],
    "Telegram-бот": [
        ("Start", "приём заявок + меню", "как консультант"),
        ("Pro", "анкета + админ-панель", "упорядочить заказы"),
        ("Max", "оплаты/интеграции/API", "автоматизация"),
    ],
    "Mini App": [
        ("Start", "форма заявки + кнопки", "быстрый запуск"),
        ("Pro", "каталог/витрина/личный кабинет", "под продажи"),
        ("Max", "оплаты + интеграции", "под продукт"),
    ],
    "Моб. приложение": [
        ("Start", "прототип/дизайн", "понять структуру"),
        ("Pro", "MVP приложение", "первая версия"),
        ("Max", "сложный функционал", "под продукт"),
    ],
}

FAQ = {
    "Как проходит работа?": [
        "1) Ты описываешь задачу и цель.",
        "2) Я показываю черновик/концепт.",
        "3) Дорабатываю до результата.",
        "4) После согласования — оплата.",
    ],
    "Сроки": [
        "Зависят от задачи и объёма.",
        "Обычно после 2–3 вопросов скажу точный срок.",
    ],
    "Оплата": [
        "⚠️ Сначала показываю работу/черновик → потом оплата.",
        "Это защищает тебя: ты видишь результат до оплаты.",
    ],
    "Что нужно от вас?": [
        "• ссылка на товар/проект (если есть)",
        "• 3–5 преимуществ/фишек",
        "• примеры конкурентов/референсы (по желанию)",
        "• дедлайн и пожелания по стилю",
    ],
}

# ---- простое хранение шагов заявки в чате ----
state = {}  # user_id -> dict(step=..., service=..., desc=..., deadline=..., budget=..., contact=...)

def is_admin(uid: int) -> bool:
    return ADMIN_ID and uid == ADMIN_ID

def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_lead(lead: dict):
    leads = load_leads()
    leads.append(lead)
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

def main_kb():
    kb = InlineKeyboardMarkup()
    if WEBAPP_URL:
        kb.add(InlineKeyboardButton("🧾 Открыть мини-ап (заявка)", web_app=WebAppInfo(url=WEBAPP_URL)))
    kb.add(InlineKeyboardButton("⚡ Быстрая заявка в чате", callback_data="quick"))
    kb.add(InlineKeyboardButton("💰 Прайс / пакеты", callback_data="price"))
    kb.add(InlineKeyboardButton("❓ FAQ / процесс", callback_data="faq"))
    kb.add(InlineKeyboardButton("🖼 Портфолио", url="https://dorm990.github.io/Design-Cards/"))
    kb.add(InlineKeyboardButton("💬 Написать Льву", url="https://t.me/dorm990"))
    return kb

def services_kb(prefix="svc:"):
    kb = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(s, callback_data=f"{prefix}{i}") for i, s in enumerate(SERVICES)]
    kb.add(*btns)
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="start"))
    return kb

def price_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    for i, s in enumerate(SERVICES):
        kb.add(InlineKeyboardButton(s, callback_data=f"price:{i}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="start"))
    return kb

def faq_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for k in FAQ.keys():
        kb.add(InlineKeyboardButton(k, callback_data=f"faq:{k}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="start"))
    return kb

def confirm_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Отправить", callback_data="send"))
    kb.add(InlineKeyboardButton("✏️ Изменить описание", callback_data="edit_desc"))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    state.pop(m.from_user.id, None)
    text = (
        "Привет! Я бот-консультант 👋\n\n"
        "Помогу оформить заявку на:\n"
        "• карточки WB/Ozon • сайты • боты • Mini App • моб. приложения\n\n"
        "⚠️ Важно: сначала показываю работу/черновик → потом оплата.\n"
        "Выбирай действие ниже 👇"
    )
    try:
        with open(ASSET_WELCOME, "rb") as f:
            bot.send_photo(m.chat.id, f, caption=text, reply_markup=main_kb())
    except:
        bot.send_message(m.chat.id, text, reply_markup=main_kb())

@bot.message_handler(commands=["myid"])
def myid(m):
    bot.reply_to(m, f"Твой ID: {m.from_user.id}")

# ---- админ-команды ----
@bot.message_handler(commands=["stats"])
def stats(m):
    if not is_admin(m.from_user.id):
        return
    leads = load_leads()
    bot.reply_to(m, f"Заявок всего: {len(leads)}")

@bot.message_handler(commands=["last"])
def last(m):
    if not is_admin(m.from_user.id):
        return
    leads = load_leads()
    if not leads:
        bot.reply_to(m, "Заявок пока нет.")
        return
    lead = leads[-1]
    bot.send_message(m.chat.id, format_lead(lead), parse_mode="Markdown")

@bot.message_handler(commands=["export"])
def export(m):
    if not is_admin(m.from_user.id):
        return
    if not os.path.exists(LEADS_FILE):
        bot.reply_to(m, "Файл заявок пока не создан.")
        return
    with open(LEADS_FILE, "rb") as f:
        bot.send_document(m.chat.id, f)

def format_lead(lead: dict) -> str:
    return (
        "🆕 *Заявка*\n\n"
        f"👤 Клиент: {lead.get('name','—')}\n"
        f"🔗 Username: {lead.get('username','—')}\n"
        f"🧷 Link: {lead.get('link','—')}\n\n"
        f"🛠 Услуга: *{lead.get('service','—')}*\n"
        f"⏱ Дедлайн: {lead.get('deadline','—')}\n"
        f"💰 Бюджет: {lead.get('budget','—')}\n\n"
        f"📝 Описание:\n{lead.get('desc','—')}\n\n"
        f"📞 Контакт:\n{lead.get('contact','—')}\n\n"
        "⚠️ Сначала показываю работу/черновик → потом оплата."
    )

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid = call.from_user.id
    data = call.data

    if data == "start":
        bot.answer_callback_query(call.id)
        fake = call.message
        fake.from_user = call.from_user
        start(fake)
        return

    if data == "quick":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Выбери услугу 👇", reply_markup=services_kb(prefix="svc:"))
        return

    if data.startswith("svc:"):
        bot.answer_callback_query(call.id)
        idx = int(data.split(":")[1])
        service = SERVICES[idx]
        state[uid] = {"step": "desc", "service": service}
        bot.send_message(
            call.message.chat.id,
            f"Ок! Услуга: *{service}*\n\n"
            "1) Опиши задачу (что нужно, ссылки/референсы, что важно, дедлайн):",
            parse_mode="Markdown"
        )
        return

    if data == "price":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Выбери услугу — покажу пакеты 👇", reply_markup=price_kb())
        return

    if data.startswith("price:"):
        bot.answer_callback_query(call.id)
        idx = int(data.split(":")[1])
        service = SERVICES[idx]
        packs = PRICING.get(service)
        if not packs:
            bot.send_message(call.message.chat.id, "Для этой услуги пакеты уточняются. Напиши в заявку — подскажу.")
            return
        lines = [f"💰 *Пакеты: {service}*\n"]
        for name, inc, forwhom in packs:
            lines.append(f"• *{name}* — {inc}\n  _{forwhom}_")
        lines.append("\n⚠️ Сначала показываю работу/черновик → потом оплата.")
        lines.append("Хочешь — подберу пакет под твою задачу. Нажми «Быстрая заявка» 👇")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("⚡ Быстрая заявка", callback_data="quick"))
        kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="start"))
        bot.send_message(call.message.chat.id, "\n".join(lines), parse_mode="Markdown", reply_markup=kb)
        return

    if data == "faq":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "FAQ / процесс работы 👇", reply_markup=faq_kb())
        return

    if data.startswith("faq:"):
        bot.answer_callback_query(call.id)
        key = data.split(":", 1)[1]
        items = FAQ.get(key, [])
        text = f"❓ *{key}*\n\n" + "\n".join([f"• {x}" for x in items]) + "\n\n⚠️ Сначала показываю работу → потом оплата."
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("⚡ Быстрая заявка", callback_data="quick"))
        kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="faq"))
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=kb)
        return

    if data == "edit_desc":
        bot.answer_callback_query(call.id)
        st = state.get(uid, {})
        st["step"] = "desc"
        state[uid] = st
        bot.send_message(call.message.chat.id, "Ок, напиши описание заново:")
        return

    if data == "cancel":
        bot.answer_callback_query(call.id)
        state.pop(uid, None)
        bot.send_message(call.message.chat.id, "Заявка отменена. Нажми /start чтобы начать заново.")
        return

    if data == "send":
        bot.answer_callback_query(call.id)
        st = state.get(uid)
        if not st or "desc" not in st:
            bot.send_message(call.message.chat.id, "Не вижу данных заявки. Нажми /start.")
            return

        u = call.from_user
        name = (u.first_name or "") + (" " + u.last_name if u.last_name else "")
        username = f"@{u.username}" if u.username else "—"
        link = f"tg://user?id={u.id}"

        lead = {
            "ts": int(time.time()),
            "name": name.strip(),
            "username": username,
            "link": link,
            "service": st.get("service", "—"),
            "desc": st.get("desc", "—"),
            "deadline": st.get("deadline", "—"),
            "budget": st.get("budget", "—"),
            "contact": st.get("contact", "Связь через Telegram"),
        }

        save_lead(lead)

        if ADMIN_ID:
            bot.send_message(ADMIN_ID, format_lead(lead), parse_mode="Markdown")

        bot.send_message(
            call.message.chat.id,
            "✅ Заявка отправлена!\n\n"
            "⚠️ Напоминание: сначала показываю работу/черновик → потом оплата.\n"
            "Я свяжусь с тобой в Telegram 🙌"
        )
        state.pop(uid, None)
        return

@bot.message_handler(content_types=["web_app_data"])
def webapp_data(m):
    # заявки из мини-апа
    try:
        data = json.loads(m.web_app_data.data)
    except:
        bot.reply_to(m, "Не получилось прочитать заявку 😕 Нажми /start и попробуй ещё раз.")
        return

    u = m.from_user
    name = (u.first_name or "") + (" " + u.last_name if u.last_name else "")
    username = f"@{u.username}" if u.username else "—"
    link = f"tg://user?id={u.id}"

    lead = {
        "ts": int(time.time()),
        "name": name.strip(),
        "username": username,
        "link": link,
        "service": data.get("service", "—"),
        "desc": data.get("desc", "—"),
        "deadline": data.get("deadline", "—"),
        "budget": data.get("budget", "—"),
        "contact": data.get("contact", "Связь через Telegram"),
    }

    save_lead(lead)
    if ADMIN_ID:
        bot.send_message(ADMIN_ID, format_lead(lead), parse_mode="Markdown")

    bot.send_message(m.chat.id,
        "✅ Заявка отправлена!\n\n⚠️ Сначала показываю работу/черновик → потом оплата.\nЯ напишу тебе в Telegram 🙌"
    )

@bot.message_handler(func=lambda m: True)
def steps(m):
    uid = m.from_user.id
    st = state.get(uid)
    if not st:
        return

    if st.get("step") == "desc":
        st["desc"] = m.text.strip()
        st["step"] = "deadline"
        state[uid] = st
        bot.send_message(m.chat.id, "2) Дедлайн (если есть). Если нет — напиши «нет»")
        return

    if st.get("step") == "deadline":
        st["deadline"] = m.text.strip()
        st["step"] = "budget"
        state[uid] = st
        bot.send_message(m.chat.id, "3) Бюджет (если есть). Если нет — напиши «не знаю»")
        return

    if st.get("step") == "budget":
        st["budget"] = m.text.strip()
        st["step"] = "contact"
        state[uid] = st
        bot.send_message(m.chat.id, "4) Контакт для связи (или «Связь через Telegram»):")
        return

    if st.get("step") == "contact":
        st["contact"] = m.text.strip()
        st["step"] = "confirm"
        state[uid] = st

        preview = (
            "Проверь заявку 👇\n\n"
            f"🛠 Услуга: {st.get('service','—')}\n"
            f"📝 Описание: {st.get('desc','—')}\n"
            f"⏱ Дедлайн: {st.get('deadline','—')}\n"
            f"💰 Бюджет: {st.get('budget','—')}\n"
            f"📞 Контакт: {st.get('contact','—')}\n\n"
            "⚠️ Сначала показываю работу → потом оплата."
        )
        bot.send_message(m.chat.id, preview, reply_markup=confirm_kb())
        return

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)



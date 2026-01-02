import os, json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")              # <-- новый токен после /revoke
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # твой id: 7236376615
WEBAPP_URL = os.getenv("WEBAPP_URL")        # ссылка на GitHub Pages

bot = telebot.TeleBot(TOKEN)

ASSET_WELCOME = "assets/welcome_banner.png"
ASSET_MENU = "assets/services_menu.png"

def start_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧾 Открыть мини-ап (заявка)", web_app=WebAppInfo(url=WEBAPP_URL)))
    kb.add(InlineKeyboardButton("🖼 Портфолио", url="https://dorm990.github.io/Design-Cards/"))
    kb.add(InlineKeyboardButton("💬 Написать Льву", url="https://t.me/dorm990"))
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    text = (
        "Привет! Я бот-консультант Льва 👋\n\n"
        "Здесь можно быстро оформить заявку на:\n"
        "• карточки WB/Ozon • сайты • боты • Mini App • моб. приложения\n\n"
        "⚠️ Важно: сначала показываю работу/черновик → потом оплата.\n"
        "Нажми кнопку ниже 👇"
    )
    try:
        with open(ASSET_WELCOME, "rb") as f:
            bot.send_photo(m.chat.id, f, caption=text, reply_markup=start_kb())
    except:
        bot.send_message(m.chat.id, text, reply_markup=start_kb())

@bot.message_handler(commands=["myid"])
def myid(m):
    bot.reply_to(m, f"Твой ID: {m.from_user.id}")

@bot.message_handler(content_types=["web_app_data"])
def webapp_data(m):
    try:
        data = json.loads(m.web_app_data.data)
    except:
        bot.reply_to(m, "Не получилось прочитать заявку 😕 Попробуй ещё раз через /start")
        return

    user = m.from_user
    name = (user.first_name or "") + (" " + user.last_name if user.last_name else "")
    username = f"@{user.username}" if user.username else "—"
    user_link = f"tg://user?id={user.id}"

    msg = (
        "🆕 *Новая заявка (Mini App)*\n\n"
        f"👤 Клиент: {name.strip()}\n"
        f"🔗 Username: {username}\n"
        f"🧷 Link: {user_link}\n\n"
        f"🛠 Услуга: *{data.get('service','—')}*\n"
        f"⏱ Дедлайн: {data.get('deadline','—')}\n"
        f"💰 Бюджет: {data.get('budget','—')}\n\n"
        f"📝 Описание:\n{data.get('desc','—')}\n\n"
        f"📞 Контакт:\n{data.get('contact','—')}\n\n"
        f"⚠️ {data.get('policy','Сначала работа → потом оплата.')}"
    )

    if ADMIN_ID:
        bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")

    bot.send_message(
        m.chat.id,
        "✅ Заявка отправлена!\n\n"
        "⚠️ Напоминание: сначала показываю работу/черновик → потом оплата.\n"
        "Я свяжусь с тобой в Telegram 🙌"
    )

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)

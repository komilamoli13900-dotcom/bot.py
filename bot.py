import telebot
import time

BOT_TOKEN = "8991830641:AAHUfV7lBaUB4uInPTXzhqQEeEAE3YSyYQ0"
ADMIN_ID = 123456789   # اینجا آیدی عددی خودتو بزار

bot = telebot.TeleBot(BOT_TOKEN)

waiting_for_receipt = {}
waiting_for_config = {}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg,
        "سلام 👋\n"
        "برای خرید کانفیگ روی دکمه زیر بزن:",
        reply_markup=menu()
    )

def menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 خرید کانفیگ", "📞 پشتیبانی")
    return markup

@bot.message_handler(func=lambda m: True)
def main(msg):
    chat_id = msg.chat.id
    text = msg.text

    if text == "🛒 خرید کانفیگ":
        bot.send_message(chat_id,
            "لطفاً مبلغ را به کارت زیر واریز کنید:\n\n"
            "💳 6274121185412365\n\n"
            "بعد از پرداخت، رسید را ارسال کنید.")
        waiting_for_receipt[chat_id] = True
        return

    if text == "📞 پشتیبانی":
        bot.send_message(chat_id, "آیدی پشتیبانی:\n@komil_pv")
        return

    if chat_id in waiting_for_receipt:
        bot.send_message(chat_id, "رسید دریافت شد. منتظر تأیید مدیر باشید.")
        bot.send_message(ADMIN_ID,
            f"📥 رسید جدید از مشتری:\n\n"
            f"ID: {chat_id}\n"
            f"پیام:\n{text}",
            reply_markup=admin_buttons(chat_id)
        )
        del waiting_for_receipt[chat_id]
        return

    if chat_id in waiting_for_config:
        user_id = waiting_for_config[chat_id]
        bot.send_message(user_id, "کانفیگ شما آماده شد:\n\n" + text)
        bot.send_message(chat_id, "برای مشتری ارسال شد ✔️")
        del waiting_for_config[chat_id]
        return

def admin_buttons(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✔️ تأیید", callback_data=f"ok_{user_id}"),
        telebot.types.InlineKeyboardButton("❌ رد", callback_data=f"no_{user_id}")
    )
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data

    if data.startswith("ok_"):
        user_id = int(data.split("_")[1])
        bot.send_message(call.message.chat.id,
            f"تأیید شد.\nکانفیگ را ارسال کن تا برای مشتری فرستاده شود.")
        waiting_for_config[call.message.chat.id] = user_id
        bot.send_message(user_id, "رسید شما تأیید شد ✔️\nلطفاً منتظر دریافت کانفیگ باشید.")
        return

    if data.startswith("no_"):
        user_id = int(data.split("_")[1])
        bot.send_message(user_id, "❌ رسید شما رد شد.")
        bot.send_message(call.message.chat.id, "رد شد.")
        return

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print("Error:", e)
        time.sleep(3)

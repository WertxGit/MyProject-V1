import telebot
from telebot import types
import random
import datetime

API_TOKEN = 'YOUR_API_TOKEN'  # Замените на ваш токен
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных пользователей
user_data = {}
titles = [
    "Новичок", "Трудяга", "Дилдоход", 
    "Легенда", "Восставший из легенд"
]

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "👋 Привет! Я помощник чата! Вот, что я умею:\n"
                                       "/banw - забанить пользователя\n"
                                       "/cmdw - список команд\n"
                                       "/warnw - выдать варн\n"
                                       "/mutew - выдать мут\n"
                                       "/profw - показать профиль пользователя\n"
                                       "/coinw - получить Верт коины\n"
                                       "/clanw - создать свой клан\n")

@bot.message_handler(commands=['cmdw'])
def cmdw_command(message):
    bot.send_message(message.chat.id, "🛠️ Список команд:\n"
                                       "/banw - Забанить пользователя\n"
                                       "/warnw - Выдать варн\n"
                                       "/mutew - Выдать мут\n"
                                       "/profw - Показать профиль\n"
                                       "/coinw - Получить Верт коины\n"
                                       "/clanw - Создать свой клан\n")

@bot.message_handler(commands=['banw'])
def ban_command(message):
    # Логика блокировки пользователя
    # Здесь может понадобиться ваша реализация
    bot.reply_to(message, "🔒 Пользователь был заблокирован!")

@bot.message_handler(commands=['warnw'])
def warn_command(message):
    # Логика выдачи варна
    bot.reply_to(message, "⚠️ Варн выдан пользователю!")

@bot.message_handler(commands=['mutew'])
def mute_command(message):
    # Логика выдачи мута
    bot.reply_to(message, "🔇 Пользователь был замучен!")

@bot.message_handler(commands=['profw'])
def profile_command(message):
    user_id = message.from_user.id
    user_profile = user_data.get(user_id, {'title': "Новичок", 'messages_count': 0, 'coins': 0})

    # Подсчет титула
    title = user_profile['title']
    messages_count = user_profile['messages_count']
    if messages_count >= 10000:
        title = titles[4]
    elif messages_count >= 4000:
        title = titles[3]
    elif messages_count >= 2500:
        title = titles[2]
    elif messages_count >= 1000:
        title = titles[1]

    response = (f"🆔 Никнейм: {message.from_user.username}\n"
                f"💰 Верт коины: {user_profile['coins']}\n"
                f"📝 Актив в чате: {messages_count} сообщений\n"
                f"🏷️ Клан: {user_profile.get('clan', 'Нет')}\n"
                f"🎖️ Титул: {title}")

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['coinw'])
def coin_command(message):
    coins = random.randint(10, 500)
    user_id = message.from_user.id

    if user_id in user_data:
        user_data[user_id]['coins'] += coins
    else:
        user_data[user_id] = {'coins': coins, 'messages_count': 0, 'title': "Новичок"}

    bot.send_message(message.chat.id, f"🎲 Вам выдано {coins} Верт коинов!")

@bot.message_handler(commands=['clanw'])
def clan_command(message):
    # Логика создания клана
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Заплатить 100 coins", callback_data="pay_clan")
    markup.add(button)
    
    bot.send_message(message.chat.id, "⚔️ Если вы хотите создать свой клан, вам придется заплатить 100 Верт коинов.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_clan")
def pay_clan_callback(call):
    user_id = call.from_user.id
    if user_id in user_data and user_data[user_id]['coins'] >= 100:
        user_data[user_id]['coins'] -= 100
        bot.send_message(call.message.chat.id, "✔️ Вы успешно создали клан!")
    else:
        bot.send_message(call.message.chat.id, "❌ У вас недостаточно Верт коинов!")

# Дополнительные обработчики для других команд...

bot.polling(none_stop=True)

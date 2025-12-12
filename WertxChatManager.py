import telebot
from telebot import types
import random

API_TOKEN = '8203019558:AAGuS6n0M7ZpnyiAuZfyrMjRg4qqLSR4i9c'  # Ваш токен
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных пользователей
user_data = {}
admin_ids = {}  # Хранит ID администраторов чата и их ранги

# Начальные данные для рангов
titles = [
    "Пользователь", "Подсос", "Модератор", 
    "Ст. Модератор", "Админ", "Создатель"
]

def has_access(user_id, required_rank):
    user_rank = user_data.get(user_id, {'rank': 0})['rank']
    return user_rank >= required_rank

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "👋 Привет! Я помощник чата! Вот, что я умею:\n"
                                       "/banw - забанить пользователя\n"
                                       "/cmdw - список команд\n"
                                       "/warnw - выдать варн\n"
                                       "/mutew - выдать мут\n"
                                       "/profw - показать профиль пользователя\n"
                                       "/coinw - получить Верт коины\n"
                                       "/clanw - создать свой клан\n"
                                       "/admw - показать список админов\n")

@bot.message_handler(commands=['cmdw'])
def cmdw_command(message):
    bot.send_message(message.chat.id, "🛠️ Список команд:\n"
                                       "/banw - Забанить пользователя (Требует ранг 3+)\n"
                                       "/warnw - Выдать варн (Требует ранг 1+)\n"
                                       "/mutew - Выдать мут (Требует ранг 1+)\n"
                                       "/profw - Показать профиль\n"
                                       "/coinw - Получить Верт коины\n"
                                       "/clanw - Создать свой клан\n"
                                       "/admw - Показать список админов\n")

@bot.message_handler(commands=['banw'])
def ban_command(message):
    if has_access(message.from_user.id, 3):
        bot.reply_to(message, "🔒 Пользователь был заблокирован!")
    else:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде!")

@bot.message_handler(commands=['warnw'])
def warn_command(message):
    if has_access(message.from_user.id, 1):
        bot.reply_to(message, "⚠️ Варн выдан пользователю!")
    else:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде!")

@bot.message_handler(commands=['mutew'])
def mute_command(message):
    if has_access(message.from_user.id, 1):
        bot.reply_to(message, "🔇 Пользователь был замучен!")
    else:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде!")

@bot.message_handler(commands=['profw'])
def profile_command(message):
    user_id = message.from_user.id
    user_profile = user_data.get(user_id, {'title': "Новичок", 'messages_count': 0, 'coins': 0, 'rank': 0})

    title = user_profile['title']
    messages_count = user_profile['messages_count']
    rank = user_profile['rank']
    
    response = (f"🆔 Никнейм: {message.from_user.username}\n"
                f"💰 Верт коины: {user_profile['coins']}\n"
                f"📝 Актив в чате: {messages_count} сообщений\n"
                f"🏷️ Ранг: {titles[rank]}\n"
                f"🏷️ Клан: {user_profile.get('clan', 'Нет')}\n")
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['coinw'])
def coin_command(message):
    coins = random.randint(10, 500)
    user_id = message.from_user.id

    if user_id in user_data:
        user_data[user_id]['coins'] += coins
    else:
        user_data[user_id] = {'coins': coins, 'messages_count': 0, 'title': "Новичок", 'rank': 0}

    bot.send_message(message.chat.id, f"🎲 Вам выдано {coins} Верт коинов!")

@bot.message_handler(commands=['clanw'])
def clan_command(message):
    user_id = message.from_user.id

    if not has_access(user_id, 0):
        bot.reply_to(message, "❌ У вас нет доступа к этой команде!")
        return

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Заплатить 100 coins", callback_data=f"pay_clan_{user_id}")
    markup.add(button)
    
    bot.send_message(message.chat.id, "⚔️ Если вы хотите создать свой клан, вам придется заплатить 100 Верт коинов.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_clan_"))
def pay_clan_callback(call):
    user_id = call.from_user.id
    creator_id = int(call.data.split("_")[2])  # Извлечь ID создателя

    if user_id != creator_id:
        bot.answer_callback_query(call.id, "❌ Эта кнопка доступна только создателю команды.")
        return

    if user_id in user_data and user_data[user_id]['coins'] >= 100:
        user_data[user_id]['coins'] -= 100
        bot.send_message(call.message.chat.id, "✔️ Вы успешно создали клан!")
    else:
        bot.send_message(call.message.chat.id, "❌ У вас недостаточно Верт коинов!")

@bot.message_handler(commands=['admw'])
def admin_command(message):
    admins = [user_id for user_id, data in user_data.items() if data['rank'] >= 4]
    admin_list = "\n".join([str(user_id) + " (Ранг: " + titles[data['rank']] + ")" for user_id in admins]) if admins else "Нет администраторов."
    bot.send_message(message.chat.id, f"👮 Список администраторов:\n{admin_list}")

@bot.message_handler(commands=['upw'])
def upgrade_command(message):
    if has_access(message.from_user.id, 4):  # Проверка, что пользователь - администратор
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
        if user_id and user_id in user_data:
            user_data[user_id]['rank'] += 1
            bot.reply_to(message, f"📈 Ранг пользователя {user_data[user_id].get('username', user_id)} увеличен до {titles[user_data[user_id]['rank']]}.")
        else:
            bot.reply_to(message, "❌ Укажите пользователя, чей ранг необходимо повысить!")
    else:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде!")

@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == message.chat.id:  # Если новый участник - это бот
            user_data[new_member.id] = {'rank': 5}  # Создатель получает ранг 5
            admin_ids[new_member.id] = True  # Добавляем создателя в администраторы

# Игнорирование неподходящих сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def ignore_message(message):
    pass  # Тут ничего не делаем, просто игнорируем

bot.polling(none_stop=True)


import telebot
from telebot import types
import random
import string

API_TOKEN = '8203019558:AAGuS6n0M7ZpnyiAuZfyrMjRg4qqLSR4i9c'  # Ваш токен
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных пользователей
user_data = {}
admin_ids = {}  # Хранит ID администраторов чата и их ранги
used_promo_codes = set()  # Множество использованных промокодов

# Начальные данные для рангов
titles = [
    "Пользователь", "Подсос", "Модератор", 
    "Ст. Модератор", "Админ", "Создатель"
]

def is_owner_or_admin(user_id):
    return user_id in admin_ids

def has_access(user_id, required_rank):
    if is_owner_or_admin(user_id):
        return True  # Всегда даем доступ владельцам и администраторам
    user_rank = user_data.get(user_id, {'rank': 0})['rank']
    return user_rank >= required_rank

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "👋 Привет! Я помощник чата! Вот, что я умею:\n"
                                       "/promow <код> - Ввести промокод\n"
                                       "/banw - забанить пользователя\n"
                                       "/cmdw - список команд\n"
                                       "/warnw - выдать варн\n"
                                       "/mutew - выдать мут\n"
                                       "/profw - показать профиль пользователя\n"
                                       "/coinw - получить Верт коины\n"
                                       "/clanjw <название> - Войти в клан\n"
                                       "/clanw - создать свой клан\n"
                                       "/admw - показать список админов\n"
                                       "/upw <юзернейм> - повысить ранг пользователя (или ответ на его сообщение)\n")

@bot.message_handler(commands=['cmdw'])
def cmdw_command(message):
    cmd_list = "🛠️ Список команд:\n"
    cmd_list += "/promow <код> - Ввести промокод\n"
    cmd_list += "/banw - Забанить пользователя (Требует ранг 3+)\n"
    cmd_list += "/warnw - Выдать варн (Требует ранг 1+)\n"
    cmd_list += "/mutew - Выдать мут (Требует ранг 1+)\n"
    cmd_list += "/profw - Показать профиль\n"
    cmd_list += "/coinw - Получить Верт коины\n"
    cmd_list += "/clanjw <название> - Войти в клан\n"
    cmd_list += "/clanw - Создать свой клан\n"
    cmd_list += "/admw - Показать список админов\n"
    cmd_list += "/upw <юзернейм> - Повысить ранг пользователя (или ответ на его сообщение)\n"
    
    bot.send_message(message.chat.id, cmd_list)

@bot.message_handler(commands=['promow'])
def promo_command(message):
    if len(message.text.split()) != 2:
        bot.send_message(message.chat.id, "❌ Используйте: /promow <код>")
        return

    promo_code = message.text.split()[1].strip()
    if promo_code in used_promo_codes:
        bot.send_message(message.chat.id, "❌ Этот промокод уже был использован.")
        return

    if promo_code == "W1LD23M":
        user_id = message.from_user.id
        coins_to_give = 50
        if user_id in user_data:
            user_data[user_id]['coins'] += coins_to_give
        else:
            user_data[user_id] = {'rank': 0, 'coins': coins_to_give, 'messages_count': 0, 'clan': None}

        used_promo_codes.add(promo_code)
        bot.send_message(message.chat.id, f"🎉 Вы получили {coins_to_give} Wert коинов!")

    else:
        bot.send_message(message.chat.id, "❌ Неверный промокод.")

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
    user_profile = user_data.get(user_id, {'rank': 0, 'coins': 0, 'messages_count': 0, 'clan': None})

    clan_name = user_profile.get('clan', 'Нет')
    response = (f"🆔 Никнейм: {message.from_user.username}\n"
                f"💰 Верт коины: {user_profile['coins']}\n"
                f"📝 Актив в чате: {user_profile['messages_count']} сообщений\n"
                f"🏷️ Ранг: {titles[user_profile['rank']]}\n"
                f"🏷️ Клан: {clan_name}\n")
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['coinw'])
def coin_command(message):
    coins = random.randint(10, 500)
    user_id = message.from_user.id

    if user_id in user_data:
        user_data[user_id]['coins'] += coins
    else:
        user_data[user_id] = {'coins': coins, 'messages_count': 0, 'rank': 0, 'clan': None}

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
        user_data[user_id]['clan'] = "Клан"  # предположительное название клана
        bot.send_message(call.message.chat.id, "✔️ Вы успешно создали клан!")
    else:
        bot.send_message(call.message.chat.id, "❌ У вас недостаточно Верт коинов!")

@bot.message_handler(commands=['clanjw'])
def join_clan_command(message):
    if len(message.text.split()) != 2:
        bot.send_message(message.chat.id, "❌ Используйте: /clanjw <название>")
        return

    clan_name = message.text.split()[1].strip()
    user_id = message.from_user.id

    # Проверка, существует ли клан (вам нужно будет реализовать свою логику для работы с кланами)
    user_data[user_id]['clan'] = clan_name
    bot.send_message(message.chat.id, f"🎉 Вы присоединились к клану '{clan_name}'!")

@bot.message_handler(commands=['admw'])
def admin_command(message):
    admins = [user_id for user_id, data in user_data.items() if data['rank'] >= 4]
    admin_list = "\n".join([f"{user_id} (Ранг: {titles[data['rank']]})" for user_id in admins]) if admins else "Нет администраторов."
    bot.send_message(message.chat.id, f"👮 Список администраторов:\n{admin_list}")

@bot.message_handler(commands=['upw'])
def upgrade_command(message):
    if is_owner_or_admin(message.from_user.id):
        user_id = None
        
        # Проверяем, был ли ответ на сообщение
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            # Получаем юзернейм из команды
            if len(message.text.split()) == 2:
                username = message.text.split()[1].strip()
                for member in bot.get_chat_administrators(message.chat.id):
                    if member.user.username and member.user.username.lower() == username.lower():
                        user_id = member.user.id
                        break

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
            user_data[new_member.id] = {'rank': 5, 'clan': None}  # Создатель получает ранг 5
            admin_ids[new_member.id] = True  # Добавляем создателя в администраторы

# Игнорирование неподходящих сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def ignore_message(message):
    pass  # Тут ничего не делаем, просто игнорируем

bot.polling(none_stop=True)


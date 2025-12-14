import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

API_TOKEN = '8128405080:AAGJxXKZ9V7Ykt4DOPl0MR8GJ7D_2lXAnGg'
bot = telebot.TeleBot(API_TOKEN)

# Хранилище данных (временно, можно заменить на базу данных)
mutes = {}  # chat_id: {user_id: until_datetime}
bans = {}   # chat_id: [user_id]
warnings = {}
user_ranks = {}  # user_id: rank_id
rank_names = [
    "Нет",  # 0
    "Младший модератор",  # 1
    "Старший модератор",  # 2
    "Младший администратор",  # 3
    "Старший администратор",  # 4
    "Создатель"  # 5
]

# Проверка, является ли пользователь администратором или повышенным ранговым

def is_admin(message):
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ['administrator', 'creator']:
            return True
        if user_ranks.get(message.from_user.id, 0) > 0:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Добавить в свой чат", url="https://t.me/" + bot.get_me().username + "?startgroup=true"))
    bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.first_name}! \nЯ чат-менеджер вертх. ", reply_markup=markup)

@bot.message_handler(commands=['commands'])
def show_commands(message):
    commands_text = "📜 Список команд:\n" \
        "/mute – выдать мут\n" \
        "/unmute – снять мут\n" \
        "/ban – забанить пользователя\n" \
        "/unban – разбанить пользователя\n" \
        "/warn – выдать предупреждение\n" \
        "/unwarn – снять предупреждение\n" \
        "/uprang [уровень] @юзернейм – повысить пользователя\n" \
        "/unrang – понизить пользователя на 1 уровень\n" \
        "/admins – показать всех админов\n" \
        "/mutelist – список замученных\n" \
        "/banlist – список забаненных\n" \
        "/commands – список всех команд"
    bot.send_message(message.chat.id, commands_text)

# --------------------
# Команды модерации
# --------------------

@bot.message_handler(commands=['mute'])
def mute(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Ответьте на сообщение пользователя.")
        return
    until_date = datetime.now() + timedelta(hours=1)
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                              can_send_messages=False, until_date=until_date)
    chat_mutes = mutes.setdefault(message.chat.id, {})
    chat_mutes[message.reply_to_message.from_user.id] = until_date
    bot.reply_to(message, "🔇 Юзер замучен на 1 час.")

@bot.message_handler(commands=['unmute'])
def unmute(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        return
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                              can_send_messages=True, until_date=0)
    mutes.get(message.chat.id, {}).pop(message.reply_to_message.from_user.id, None)
    bot.reply_to(message, "🔈 Юзер размучен.")

@bot.message_handler(commands=['ban'])
def ban(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        return
    bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    bans.setdefault(message.chat.id, []).append(message.reply_to_message.from_user.id)
    bot.reply_to(message, "🔒 Юзер забанен.")

@bot.message_handler(commands=['unban'])
def unban(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        return
    bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    if message.reply_to_message.from_user.id in bans.get(message.chat.id, []):
        bans[message.chat.id].remove(message.reply_to_message.from_user.id)
    bot.reply_to(message, "🔓 Юзер разбанен.")

@bot.message_handler(commands=['warn'])
def warn(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        return
    uid = str(message.reply_to_message.from_user.id)
    warnings[uid] = warnings.get(uid, 0) + 1
    bot.reply_to(message, f"⚠️ Выдано предупреждение. Всего: {warnings[uid]}")

@bot.message_handler(commands=['unwarn'])
def unwarn(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        return
    uid = str(message.reply_to_message.from_user.id)
    if warnings.get(uid):
        warnings[uid] -= 1
        bot.reply_to(message, f"✅ Предупреждение удалено. Осталось: {warnings[uid]}")

# --------------------
# Повышения
# --------------------
@bot.message_handler(commands=['uprang'])
def promote_user(message):
    if not is_admin(message):
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "⚠️ Использование: /uprang [1-5] @username\nПример: /uprang 2 @user")
        return
    try:
        level = int(parts[1])
        if level < 1 or level > 5:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ Уровень должен быть от 1 до 5.")
        return

    username = parts[2].lstrip('@')

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        user_ranks[target_id] = level
        bot.send_message(message.chat.id, f"✅ Пользователь @{username} повышен до ранга: {rank_names[level]}")
    else:
        bot.send_message(message.chat.id, "⚠️ Повышение возможно только ответом на сообщение пользователя.")


# --------------------
# Кто админ
# --------------------

@bot.message_handler(commands=['admins'])
def list_admins(message):
    if not is_admin(message):
        return
    try:
        chat_id = message.chat.id
        tg_admins = bot.get_chat_administrators(chat_id)
        custom_admins = []

        # Повышенные через ранги
        for uid, rank in user_ranks.items():
            if rank > 0:
                try:
                    user = bot.get_chat_member(chat_id, uid).user
                    name = f"{user.first_name or ''} (@{user.username})"
                    custom_admins.append(f"👤 {name} — {rank_names[rank]}")
                except:
                    continue

        text = "👮 Telegram-администраторы:\n"
        for admin in tg_admins:
            user = admin.user
            name = f"{user.first_name or ''} (@{user.username})"
            text += f"👤 {name}\n"

        if custom_admins:
            text += "\n🏅 Повышенные через бот:\n" + "\n".join(custom_admins)

        bot.send_message(chat_id, text)
    except Exception as e:
        bot.reply_to(message, "❌ Не удалось получить список админов.")


# --------------------
# Списки мутов и банов
# --------------------

@bot.message_handler(commands=['mutelist'])
def mute_list(message):
    if not is_admin(message):
        return
    chat_mutes = mutes.get(message.chat.id, {})
    if not chat_mutes:
        bot.reply_to(message, "🔇 Список мутов пуст.")
        return
    text = "🔇 Замученные пользователи:\n"
    for uid, until in chat_mutes.items():
        try:
            user = bot.get_chat_member(message.chat.id, uid).user
            text += f"👤 {user.first_name} (@{user.username}) — до {until.strftime('%H:%M %d.%m')}\n"
        except:
            continue
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['banlist'])
def ban_list(message):
    if not is_admin(message):
        return
    chat_bans = bans.get(message.chat.id, [])
    if not chat_bans:
        bot.reply_to(message, "🚫 Список банов пуст.")
        return
    text = "🚫 Забаненные пользователи:\n"
    for uid in chat_bans:
        try:
            user = bot.get_chat_member(message.chat.id, uid).user
            text += f"👤 {user.first_name} (@{user.username})\n"
        except:
            continue
    bot.send_message(message.chat.id, text)
    #----------------------
    # Снять админ тг
    #----------------------
@bot.message_handler(commands=['unrang'])
def demote_user(message):
    if not is_admin(message):
        return
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Используйте команду ответом на сообщение пользователя.")
        return

    target_id = message.reply_to_message.from_user.id
    current_rank = user_ranks.get(target_id, 0)

    if current_rank <= 0:
        bot.reply_to(message, "ℹ️ У пользователя нет админ-ранга.")
        return

    new_rank = current_rank - 1
    user_ranks[target_id] = new_rank
    if new_rank == 0:
        bot.reply_to(message, "🔻 Пользователь понижен до обычного уровня.")
    else:
        bot.reply_to(message, f"🔻 Пользователь понижен до ранга: {rank_names[new_rank]}")

# --------------------
# Запуск
# --------------------
print("Bot is running...")
bot.infinity_polling()  
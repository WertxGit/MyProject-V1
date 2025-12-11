import telebot
import random
import time
import logging
import json
import os

API_TOKEN = '8203019558:AAGuS6n0M7ZpnyiAuZfyrMjRg4qqLSR4i9c'
DATA_FILE = 'DexterSimuls.json'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

# Хранилище данных о пользователях
user_data = {}

# Время последнего использования команд
last_kill_time = {}
last_work_time = {}

# Функция загрузки данных из файла
def load_user_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    else:
        user_data = {}

# Функция сохранения данных в файл
def save_user_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

# Функция получения данных пользователя
def get_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {"kills": 0, "coins": 0}
    return user_data[str(user_id)]

# Команда /Dexkill
@bot.message_handler(commands=['Dexkill'])
def dexkill(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # Проверка времени последнего использования команды
        if last_kill_time.get(user_id, 0) + 300 > current_time:
            bot.reply_to(message, "⏳ Можно использовать команду раз в 5 минут.")
            return

        last_kill_time[user_id] = current_time

        kill_success = random.choices([True, False], weights=[70, 30], k=1)[0]  # 70% шанс на успех
        kills = 0

        if kill_success:
            kills = 1
            # Дополнительный шанс на дополнительные киллы
            if random.random() < 0.45:
                kills += 1
            if random.random() < 0.25:
                kills += 1

        user = get_user_data(user_id)
        user['kills'] += kills
        save_user_data()  # Сохранение данных
        bot.reply_to(message, f"💥 Вы убили {kills} человека(ов)! Всего убийств: {user['kills']}")
    except Exception as e:
        logging.error(f"Error in /Dexkill command: {e}")

# Команда /Dexwork
@bot.message_handler(commands=['Dexwork'])
def dexwork(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # Проверка времени последнего использования команды
        if last_work_time.get(user_id, 0) + 1800 > current_time:
            bot.reply_to(message, "⏳ Можно использовать команду раз в 30 минут.")
            return

        last_work_time[user_id] = current_time

        earnings = random.randint(100, 3000)
        user = get_user_data(user_id)
        user['coins'] += earnings
        save_user_data()  # Сохранение данных
        bot.reply_to(message, f"🧑‍💼 Декстер отработал и заработал {earnings} монет! Всего монет: {user['coins']}")
    except Exception as e:
        logging.error(f"Error in /Dexwork command: {e}")

# Команда /Dexcmd
@bot.message_handler(commands=['Dexcmd'])
def dexcmd(message):
    try:
        commands_list = (
            "📜 Список команд:\n"
            "/Dexkill - убить человека 💥\n"
            "/Dexwork - Декстер идёт на работу 🧑‍💼\n"
            "/Dexcmd - показать команды 📜\n"
            "/DexterP - посмотреть профиль 👤"
        )
        bot.reply_to(message, commands_list)
    except Exception as e:
        logging.error(f"Error in /Dexcmd command: {e}")

# Команда /DexterP
@bot.message_handler(commands=['DexterP'])
def dexter_profile(message):
    try:
        user_id = message.from_user.id
        user = get_user_data(user_id)

        kills = user['kills']
        coins = user['coins']

        if kills < 1:
            rank = "новичок"
        elif kills < 5:
            rank = "пента киллер"
        elif kills < 20:
            rank = "альфа киллер"
        elif kills < 50:
            rank = "серийный убийца"
        elif kills < 100:
            rank = "Мясник из бэй-харбор"
        else:
            rank = "Мясник из бэй-харбор"

        profile_info = (
            f"👤 Количество убийств: {kills}\n"
            f"🏅 Звание: {rank}\n"
            f"💰 Монеты: {coins}"
        )
        bot.reply_to(message, profile_info)
    except Exception as e:
        logging.error(f"Error in /DexterP command: {e}")

# Игнорирование остальных сообщений
@bot.message_handler(func=lambda message: True)
def ignore_message(message):
    pass

# Главная функция для запуска бота
if __name__ == '__main__':
    load_user_data()  # Загрузка данных при запуске
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Bot stopped due to error: {e}")
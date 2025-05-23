# ovoshi.py/bot_handler.py

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv(dotenv_path="ovoshi.py/config.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

USERS_FILE = "data/users.json"
AUTHORIZED_ADMINS = set()

# --- Автоматическая подписка ---
@dp.message()
async def auto_subscribe(message: types.Message):
    user_id = message.from_user.id
    users = load_users()

    if user_id not in users:
        users.append(user_id)
        save_users(users)
        await message.answer("Вы подписаны на уведомления о занятиях!")

# --- Авторизация админа ---
@dp.message(Command("login"))
async def cmd_login(message: types.Message):
    await message.answer("Введите пароль для авторизации:")

    @dp.message()
    async def check_password(msg: types.Message):
        entered = msg.text.strip()
        if entered == ADMIN_PASSWORD:
            AUTHORIZED_ADMINS.add(msg.from_user.id)
            await msg.answer("✅ Вы вошли как админ. Доступны команды управления.")
        else:
            await msg.answer("❌ Неверный пароль.")

# --- Команда /new_lesson ---
@dp.message(Command("new_lesson"))
async def new_lesson(message: types.Message):
    if message.from_user.id not in AUTHORIZED_ADMINS:
        await message.answer("⚠️ Нет доступа.")
        return

    await message.answer("Введите дату и время занятия:\nФормат: ДД.ММ.ГГГГ ЧЧ:ММ")

    @dp.message()
    async def handle_time(msg: types.Message):
        try:
            lesson_time = datetime.strptime(msg.text.strip(), "%d.%m.%Y %H:%M")
            users = load_users()

            for user_id in users:
                try:
                    await bot.send_message(
                        user_id,
                        f"🔔 Занятие состоится {lesson_time.strftime('%d.%m.%Y %H:%M')}"
                    )
                except Exception as e:
                    print(f"Ошибка отправки пользователю {user_id}: {e}")

            await msg.answer("✅ Уведомления разосланы.")
        except ValueError:
            await msg.answer("❌ Неверный формат даты.")

# --- Работа с пользователями ---
def load_users():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

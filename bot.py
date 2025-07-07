from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("💬 Оставить отзыв"))
    kb.add(KeyboardButton("💡 Предложить идею"))
    await message.answer("Привет! Я бот кофейни AV COFFEE ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

# Меню — 2 опции
@dp.message_handler(lambda message: message.text == "📋 Меню")
async def menu_options(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📖 Посмотреть меню"))
    kb.add(KeyboardButton("➕ Добавить в меню"))
    kb.add(KeyboardButton("⬅️ Назад"))
    await message.answer("Выбери действие:", reply_markup=kb)

# Посмотреть меню
@dp.message_handler(lambda message: message.text == "📖 Посмотреть меню")
async def show_menu(message: types.Message):
    await message.answer("☕ Наше меню:\n— Эспрессо — 150₽\n— Капучино — 200₽\n— Чизкейк — 270₽")

# Добавить в меню
@dp.message_handler(lambda message: message.text == "➕ Добавить в меню")
async def suggest_menu_item(message: types.Message):
    await message.answer("Напиши, что бы ты хотел(а) видеть в нашем меню. 👇")

# Оставить отзыв
@dp.message_handler(lambda message: message.text == "💬 Оставить отзыв")
async def leave_feedback(message: types.Message):
    await message.answer("Мы будем рады твоему отзыву! Напиши его ниже 👇")

# Предложить идею
@dp.message_handler(lambda message: message.text == "💡 Предложить идею")
async def suggest_idea(message: types.Message):
    await message.answer("У тебя есть идея? Пиши сюда — мы читаем каждое сообщение 👇")

# Назад
@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await send_welcome(message)

# Обработка любых сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"{message.from_user.first_name}"
    user_msg = message.text

    await message.answer("Спасибо! Мы получили твоё сообщение. ☕")

    if ADMIN_CHAT_ID != 0:
        forward_text = f"📩 Новое сообщение от {username}:\n{user_msg}"
        try:
            await bot.send_message(ADMIN_CHAT_ID, forward_text)
        except Exception as e:
            print(f"Ошибка при пересылке сообщения: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

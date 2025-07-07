from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Меню с кнопками
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🍽 Меню"))
main_kb.add(KeyboardButton("💬 Написать отзыв"), KeyboardButton("📩 Предложение в меню"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот кофейни AV COFFEE ☕\nЧем могу быть полезен?", reply_markup=main_kb)

@dp.message_handler(lambda msg: msg.text == "🍽 Меню")
async def send_menu(message: types.Message):
    menu = [
        {"name": "Чизкейк", "price": "270₽", "file": InputFile("чизкейк.jpg")},
        {"name": "Круассан с лососем", "price": "420₽", "file": InputFile("круасан.jpg")},
        {"name": "Капучино", "price": "200₽", "file": InputFile("капучино.jpg")},
        {"name": "Эспрессо", "price": "150₽", "file": InputFile("эспрессо.jpg")},
    ]
    for item in menu:
        caption = f"{item['name']} — {item['price']}"
        await bot.send_photo(message.chat.id, item['file'], caption=caption)

@dp.message_handler(lambda msg: msg.text == "💬 Написать отзыв")
async def request_feedback(message: types.Message):
    await message.answer("✍️ Напиши свой отзыв здесь 👇")
    dp.register_message_handler(handle_feedback, content_types=types.ContentTypes.TEXT, state=None)

@dp.message_handler(lambda msg: msg.text == "📩 Предложение в меню")
async def request_suggestion(message: types.Message):
    await message.answer("📬 Напиши, что бы ты хотел добавить в меню 👇")
    dp.register_message_handler(handle_suggestion, content_types=types.ContentTypes.TEXT, state=None)

async def handle_feedback(message: types.Message):
    text = message.text
    username = message.from_user.username or f"{message.from_user.first_name}"
    await message.answer("Спасибо за отзыв! 💚")
    if ADMIN_CHAT_ID:
        msg = f"📨 *Отзыв* от @{username}:{text}"
        await bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="Markdown")
    dp.message_handlers.unregister(handle_feedback)

async def handle_suggestion(message: types.Message):
    text = message.text
    username = message.from_user.username or f"{message.from_user.first_name}"
    await message.answer("Спасибо! Мы рассмотрим твоё предложение 🧠")
    if ADMIN_CHAT_ID:
        msg = f"📌 *Предложение в меню* от @{username}:
{text}"
        await bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="Markdown")
    dp.message_handlers.unregister(handle_suggestion)

@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Выбери действие с помощью кнопок ниже 👇")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)

# Главное меню
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("✏️ Написать отзыв"))
    kb.add(KeyboardButton("💡 Предложение в меню"))
    await message.answer("Привет! Я бот кофейни *AV COFFEE* ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

# Показать фотоменю
@dp.message_handler(lambda message: message.text == "📋 Меню")
async def show_menu(message: types.Message):
    await bot.send_photo(message.chat.id, InputFile("чизкейк.jpg"), caption="🍰 *Чизкейк* — 270Р", parse_mode="MarkdownV2")
    await bot.send_photo(message.chat.id, InputFile("круасан.jpg"), caption="🥐 *Круассан с лососем* — 390Р", parse_mode="MarkdownV2")
    await bot.send_photo(message.chat.id, InputFile("капучино.jpg"), caption="☕ *Капучино* — 200Р", parse_mode="MarkdownV2")
    await bot.send_photo(message.chat.id, InputFile("эспрессо.jpg"), caption="☕ *Эспрессо* — 150Р", parse_mode="MarkdownV2")

# Оставить отзыв
@dp.message_handler(lambda message: message.text == "✏️ Написать отзыв")
async def get_feedback(message: types.Message):
    await message.answer("Будем рады услышать твой отзыв! Напиши его в ответ 👇")
    dp.register_message_handler(handle_feedback, content_types=types.ContentTypes.TEXT, state=None)

async def handle_feedback(message: types.Message):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")  # Экранирование
    await message.answer("Спасибо за отзыв! 💚")
    if ADMIN_CHAT_ID:
        msg = f"📨 *Отзыв* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="MarkdownV2")
    dp.unregister_message_handler(handle_feedback, content_types=types.ContentTypes.TEXT, state=None)

# Добавить предложение в меню
@dp.message_handler(lambda message: message.text == "💡 Предложение в меню")
async def get_suggestion(message: types.Message):
    await message.answer("Напиши, что ты хотел бы добавить в меню 👇")
    dp.register_message_handler(handle_suggestion, content_types=types.ContentTypes.TEXT, state=None)

async def handle_suggestion(message: types.Message):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")  # Экранирование
    await message.answer("Спасибо за идею! Мы рассмотрим её 🚀")
    if ADMIN_CHAT_ID:
        msg = f"🧠 *Предложение* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="MarkdownV2")
    dp.unregister_message_handler(handle_suggestion, content_types=types.ContentTypes.TEXT, state=None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

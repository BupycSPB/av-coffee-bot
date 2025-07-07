from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния FSM
class Form(StatesGroup):
    feedback = State()
    suggestion = State()

# /start — главное меню
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("✏️ Написать отзыв"))
    kb.add(KeyboardButton("💡 Предложение в меню"))
    await message.answer("Привет! Я бот кофейни *AV COFFEE* ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

# Показать фотоменю
@dp.message_handler(lambda message: message.text == "📋 Меню")
async def show_menu(message: types.Message):
    items = [
        ("чизкейк.jpg", "🍰 *Чизкейк* — 270Р"),
        ("круасан.jpg", "🥐 *Круассан с лососем* — 390Р"),
        ("капучино.jpg", "☕ *Капучино* — 200Р"),
        ("эспрессо.jpg", "☕ *Эспрессо* — 150Р"),
    ]
    for file, caption in items:
        await bot.send_photo(message.chat.id, InputFile(file), caption=caption)

# Начало ввода отзыва
@dp.message_handler(lambda message: message.text == "✏️ Написать отзыв")
async def start_feedback(message: types.Message):
    await message.answer("Будем рады услышать твой отзыв! Напиши его ниже.", reply_markup=ReplyKeyboardRemove())
    await Form.feedback.set()

# Обработка отзыва
@dp.message_handler(state=Form.feedback, content_types=types.ContentTypes.TEXT)
async def handle_feedback(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")
    await message.answer("Спасибо за отзыв! 💚")
    if ADMIN_CHAT_ID:
        msg = f"📨 *Отзыв* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await state.finish()

# Начало ввода предложения
@dp.message_handler(lambda message: message.text == "💡 Предложение в меню")
async def start_suggestion(message: types.Message):
    await message.answer("Напиши, что ты хотел бы предложить в меню.", reply_markup=ReplyKeyboardRemove())
    await Form.suggestion.set()

# Обработка предложения
@dp.message_handler(state=Form.suggestion, content_types=types.ContentTypes.TEXT)
async def handle_suggestion(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")
    await message.answer("Спасибо за предложение! Мы рассмотрим её 🚀")
    if ADMIN_CHAT_ID:
        msg = f"🧠 *Предложение* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

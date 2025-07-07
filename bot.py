from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

# Состояния для FSM
class Form(StatesGroup):
    feedback = State()
    suggestion = State()

# /start — главное меню
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Показать меню"))
    kb.add(KeyboardButton("✏️ Оставить отзыв"))
    kb.add(KeyboardButton("💡 Предложить идею"))
    await message.answer(
        "Привет! Я бот кофейни *AV COFFEE* ☕\nВыбери действие:",
        reply_markup=kb
    )

# Текстовое меню
@dp.message_handler(lambda m: m.text == "📋 Показать меню")
async def text_menu(message: types.Message):
    menu_text = (
        "🍰 *Чизкейк* — 270Р\n"
        "🥐 *Круассан с лососем* — 390Р\n"
        "☕ *Капучино* — 200Р\n"
        "☕ *Эспрессо* — 150Р"
    )
    await message.answer(menu_text, parse_mode="MarkdownV2")

# Запуск ввода отзыва
@dp.message_handler(lambda m: m.text == "✏️ Оставить отзыв")
async def start_feedback(message: types.Message):
    await message.answer(
        "Будем рады услышать твой отзыв! Напиши его ниже.",
        reply_markup=ReplyKeyboardRemove()
    )
    await Form.feedback.set()

# Обработка отзыва
@dp.message_handler(state=Form.feedback, content_types=types.ContentTypes.TEXT)
async def process_feedback(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*")
    await message.answer("Спасибо за отзыв! 💚")
    if ADMIN_CHAT_ID:
        notification = f"📨 *Отзыв* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=notification)
    await state.finish()

# Запуск ввода предложения
@dp.message_handler(lambda m: m.text == "💡 Предложить идею")
async def start_suggestion(message: types.Message):
    await message.answer(
        "Напиши, что ты хотел бы предложить в меню.",
        reply_markup=ReplyKeyboardRemove()
    )
    await Form.suggestion.set()

# Обработка предложения
@dp.message_handler(state=Form.suggestion, content_types=types.ContentTypes.TEXT)
async def process_suggestion(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    text = message.text.replace("_", "\\_").replace("*", "\\*")
    await message.answer("Спасибо за идею! Мы рассмотрим её 🚀")
    if ADMIN_CHAT_ID:
        notification = f"🧠 *Предложение* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=notification)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

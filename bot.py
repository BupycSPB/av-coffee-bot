from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM для отзывов
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

# Главное меню
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("✏️ Написать отзыв"))
    kb.add(KeyboardButton("💡 Предложение в меню"))
    await message.answer("Привет! Я бот кофейни AV COFFEE ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

# Фотоменю
@dp.message_handler(lambda message: message.text == "📋 Меню")
async def show_menu(message: types.Message):
    await bot.send_photo(message.chat.id, InputFile("чизкейк.jpg"), caption="🍰 Чизкейк — 270Р")
    await bot.send_photo(message.chat.id, InputFile("круасан.jpg"), caption="🥐 Круассан с лососем — 390Р")
    await bot.send_photo(message.chat.id, InputFile("капучино.jpg"), caption="☕ Капучино — 200Р")
    await bot.send_photo(message.chat.id, InputFile("эспрессо.jpg"), caption="☕ Эспрессо — 150Р")

# Оставить отзыв — старт
@dp.message_handler(lambda message: message.text == "✏️ Написать отзыв")
async def get_feedback(message: types.Message):
    await message.answer("Будем рады услышать твой отзыв! Напиши его в ответ 👇")
    await FeedbackState.waiting_for_feedback.set()

# Оставить отзыв — обработка
@dp.message_handler(state=FeedbackState.waiting_for_feedback, content_types=types.ContentTypes.TEXT)
async def handle_feedback(message: types.Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name
    text = message.text
    await message.answer("Спасибо за отзыв! 💚")
    if ADMIN_CHAT_ID:
        msg = f"📨 *Отзыв* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await state.finish()

# Предложить идею (старый способ — можно заменить на FSM аналогично)
@dp.message_handler(lambda message: message.text == "💡 Предложение в меню")
async def get_suggestion(message: types.Message):
    await message.answer("Напиши, что ты хотел бы добавить в меню 👇")
    dp.register_message_handler(handle_suggestion, content_types=types.ContentTypes.TEXT, state=None)

async def handle_suggestion(message: types.Message):
    username = message.from_user.username or message.from_user.full_name
    text = message.text
    await message.answer("Спасибо за идею! Мы рассмотрим её 🚀")
    if ADMIN_CHAT_ID:
        msg = f"🧠 *Предложение* от @{username}:\n{text}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    dp.unregister_message_handler(handle_suggestion, content_types=types.ContentTypes.TEXT, state=None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

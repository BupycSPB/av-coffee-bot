from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния пользователя
class Form(StatesGroup):
    feedback = State()
    menu_suggestion = State()
    idea = State()

# Главное меню
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("💬 Оставить отзыв"))
    kb.add(KeyboardButton("💡 Предложить идею"))
    await message.answer("Привет! Я бот кофейни AV COFFEE ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

# Меню → варианты
@dp.message_handler(lambda message: message.text == "📋 Меню", state='*')
async def menu_options(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📖 Посмотреть меню"))
    kb.add(KeyboardButton("➕ Добавить в меню"))
    kb.add(KeyboardButton("⬅️ Назад"))
    await message.answer("Выбери действие:", reply_markup=kb)

# Посмотреть меню
@dp.message_handler(lambda message: message.text == "📖 Посмотреть меню", state='*')
async def show_menu(message: types.Message):
    await message.answer("☕ Наше меню:\n— Эспрессо — 150₽\n— Капучино — 200₽\n— Чизкейк — 270₽")

# ➕ Добавить в меню
@dp.message_handler(lambda message: message.text == "➕ Добавить в меню", state='*')
async def suggest_menu_item(message: types.Message):
    await Form.menu_suggestion.set()
    await message.answer("Что бы ты хотел(а) добавить в меню? Напиши ниже 👇")

# 💬 Оставить отзыв
@dp.message_handler(lambda message: message.text == "💬 Оставить отзыв", state='*')
async def leave_feedback(message: types.Message):
    await Form.feedback.set()
    await message.answer("Мы будем рады твоему отзыву! Напиши его сюда 👇")

# 💡 Предложить идею
@dp.message_handler(lambda message: message.text == "💡 Предложить идею", state='*')
async def suggest_idea(message: types.Message):
    await Form.idea.set()
    await message.answer("У тебя есть идея? Пиши сюда — мы читаем каждое сообщение 👇")

# ⬅️ Назад
@dp.message_handler(lambda message: message.text == "⬅️ Назад", state='*')
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()
    await send_welcome(message, state)

# Обработка отзывов, предложений и идей
@dp.message_handler(state=Form.feedback)
async def handle_feedback(message: types.Message, state: FSMContext):
    await state.finish()
    await process_message(message, "📝 Новый отзыв")

@dp.message_handler(state=Form.menu_suggestion)
async def handle_menu_suggestion(message: types.Message, state: FSMContext):
    await state.finish()
    await process_message(message, "🍽️ Предложение по меню")

@dp.message_handler(state=Form.idea)
async def handle_idea(message: types.Message, state: FSMContext):
    await state.finish()
    await process_message(message, "💡 Новая идея")

# Обработка прочих сообщений
@dp.message_handler()
async def handle_unknown(message: types.Message):
    await message.answer("Спасибо! Мы получили твоё сообщение. ☕")

# Отправка в админ-группу
async def process_message(message: types.Message, title: str):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    user_text = message.text
    await message.answer("Спасибо! Мы получили твоё сообщение. ☕")

    if ADMIN_CHAT_ID != 0:
        text = f"{title} от {username}:\n{user_text}"
        try:
            await bot.send_message(ADMIN_CHAT_ID, text)
        except Exception as e:
            print(f"Ошибка при отправке сообщения в группу: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

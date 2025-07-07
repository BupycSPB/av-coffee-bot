from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import InputFile
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
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"))
    kb.add(KeyboardButton("💬 Оставить отзыв"))
    kb.add(KeyboardButton("💡 Предложить идею"))
    return kb

# Вложенное меню ("папка" меню)
def menu_submenu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📸 Посмотреть меню с фото"))
    kb.add(KeyboardButton("📜 Посмотреть меню без фото"))
    kb.add(KeyboardButton("➕ Добавить пожелание по меню"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# /start — запуск/возврат в главное меню
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет! Я бот кофейни AV COFFEE ☕\nЧто бы ты хотел сделать?",
        reply_markup=main_menu()
    )

# 📋 Меню — переход во вложенное меню
@dp.message_handler(lambda message: message.text == "📋 Меню", state='*')
async def menu_options(message: types.Message, state: FSMContext):
    await message.answer("Что интересует?", reply_markup=menu_submenu())

# 📸 Посмотреть меню с фото
@dp.message_handler(lambda message: message.text == "📸 Посмотреть меню с фото", state='*')
async def show_menu_photos(message: types.Message):
    items = [
        ("pictures/чизкейк.jpg", "🍰 Чизкейк — 270₽"),
        ("pictures/круасан.jpg", "🥐 Круассан с лососем — 390₽"),
        ("pictures/капучино.jpg", "☕ Капучино — 200₽"),
        ("pictures/эспрессо.jpg", "☕ Эспрессо — 150₽"),
    ]
    for filename, caption in items:
        try:
            await bot.send_photo(message.chat.id, InputFile(filename), caption=caption)
        except Exception as e:
            await message.answer(f"Не удалось отправить {filename}: {e}")

# 📜 Посмотреть меню без фото
@dp.message_handler(lambda message: message.text == "📜 Посмотреть меню без фото", state='*')
async def show_menu_text(message: types.Message):
    try:
        with open("menu.txt", "r", encoding="utf-8") as f:
            menu = f.read()
    except FileNotFoundError:
        menu = "Меню пока не заполнено."
    await message.answer(f"☕ Наше меню:\n{menu}")

# ➕ Добавить пожелание по меню
@dp.message_handler(lambda message: message.text == "➕ Добавить пожелание по меню", state='*')
async def suggest_menu_item(message: types.Message):
    await Form.menu_suggestion.set()
    await message.answer("Что бы ты хотел(а) добавить или предложить по меню? Напиши ниже 👇")

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

# ⬅️ Назад — возвращает в главное меню
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

# Прочие сообщения
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

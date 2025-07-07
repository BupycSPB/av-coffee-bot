from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))  # ID группы для уведомлений

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📋 Меню"), KeyboardButton("📝 Сделать заказ"))
    kb.add(KeyboardButton("💬 Оставить отзыв"))
    await message.answer("Привет! Я бот кофейни AV COFFEE ☕\nЧто бы ты хотел сделать?", reply_markup=kb)

@dp.message_handler(lambda message: message.text == "📋 Меню")
async def show_menu(message: types.Message):
    await message.answer("☕ Наше меню:\n— Эспрессо — 150₽\n— Капучино — 200₽\n— Чизкейк — 270₽")

@dp.message_handler(lambda message: message.text == "📝 Сделать заказ")
async def make_order(message: types.Message):
    await message.answer("Отправь, пожалуйста, свой заказ в свободной форме. Мы подтвердим его вручную.")

@dp.message_handler(lambda message: message.text == "💬 Оставить отзыв")
async def leave_feedback(message: types.Message):
    await message.answer("Будем рады услышать твой отзыв! Просто напиши его в ответ 👇")

@dp.message_handler()
async def handle_input(message: types.Message):
    text = message.text
    username = message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    await message.answer("Спасибо! Мы получили твоё сообщение. ☕")

    if ADMIN_CHAT_ID != 0:
        msg = f"📩 Новое сообщение от @{username}:\n{text}"
        try:
            await bot.send_message(ADMIN_CHAT_ID, msg)
        except Exception as e:
            print(f"Ошибка при отправке в админ-группу: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

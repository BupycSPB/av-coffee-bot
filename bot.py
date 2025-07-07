from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("OTZYVY", "0"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(lambda message: message.chat.type == 'private')
async def handle_feedback(message: types.Message):
    text = message.text
    username = message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    await message.reply("Спасибо! Мы получили твоё сообщение. ☕")
    if ADMIN_CHAT_ID != 0:
        msg = f"📩 Новый отзыв от @{username}:\n{text}"
        try:
            await bot.send_message(ADMIN_CHAT_ID, msg)
        except Exception as e:
            print(f"Ошибка при отправке в админ-группу: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

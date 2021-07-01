from aiogram import types

from filters import IsForwarded
from loader import dp


@dp.message_handler(IsForwarded(), content_types=types.ContentType.ANY)
async def get_channel_info(message: types.Message):
    await message.answer(f"Сообщение прислано из канала {message.forward_from_chat.title}. \n"
                         f"Username: @{message.forward_from_chat.username}\n"
                         f"ID: {message.forward_from_chat.id}")

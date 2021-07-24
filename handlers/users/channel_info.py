from aiogram import types

from data.config import CHANNELS
from filters import IsForwarded
from keyboards.inline.keyboards import keyboard_subscribe
from loader import bot
from loader import dp
from utils.misc import subscription


# Получение информации о канале, если сообщение переслано из него
@dp.message_handler(IsForwarded(), content_types=types.ContentType.ANY)
async def get_channel_info(message: types.Message):
    await message.answer(f"Сообщение прислано из канала {message.forward_from_chat.title}. \n"
                         f"Username: @{message.forward_from_chat.username}\n"
                         f"ID: {message.forward_from_chat.id}")


# Обработка сообщения, если пользователь хочет подписаться на канал
@dp.callback_query_handler(text='channel')
async def subscribe_channel(call: types.CallbackQuery):
    await call.answer(cache_time=60)

    await call.message.answer('Чтобы получить реферальную ссылку, '
                              'необходимо подписаться на канал @udemy_final_project',
                              reply_markup=keyboard_subscribe)


# Проверка подписки на канал
@dp.callback_query_handler(text='check_subs')
async def checker(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    result = str()
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id,
                                          channel=channel)
        channel = await bot.get_chat(channel)
        if status:
            result += f'Подписка на канал <b>{channel.title}</b> оформлена!\n\n'
        else:
            invite_link = await channel.export_invite_link()
            result += (f'Подписка на канал <b>{channel.title}</b> не оформлена! '
                       f'<a href="{invite_link}">Нужно подписаться.</a>\n\n')

    await call.message.answer(result, disable_web_page_preview=True)

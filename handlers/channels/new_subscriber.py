import logging

from aiogram import types

from loader import dp


@dp.channel_post_handler()
async def new_sub(message: types.Message):
    logging.info(message.text)

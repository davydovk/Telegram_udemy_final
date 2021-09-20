import asyncio

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from handlers.users.start import db
from keyboards.inline.callbackdata_factory import buy_item, edit_item
from loader import dp, bot
from utils.db_api import database, db_commands, models


@dp.message_handler(commands=['items'])
async def show_items(message: Message):
    # Достаем товары из базы данных
    # all_items = await db.show_items()
    all_items = await db.show_items()

    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = f'<b>Товар</b> \t№{id}: {item.name}\n' \
               f'<b>Описание</b> \t№{id}: {item.description}\n' \
               f'<b>Цена:</b> \t{item.price:,}\n'
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text="Описание", callback_data=edit_item.new(item_id=item.id))
                ],
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text="Купить", callback_data=buy_item.new(item_id=item.id))
                ],
            ]
        )

        await message.answer_photo(item.photo, caption=item.name, reply_markup=markup)
        # await message.answer(text.format(id=item.id,
        #                                  name=item.name,
        #                                  photo=item.photo,
        #                                  description=item.description,
        #                                  price=item.price / 100), reply_markup=markup)
        await asyncio.sleep(0.3)


@dp.callback_query_handler(edit_item.filter())
async def get_description(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    item_id = callback_data.get('item_id')
    item_id = int(item_id) - 1
    all_items = await db.show_items()
    item = all_items[item_id]
    await call.message.answer(item.description)

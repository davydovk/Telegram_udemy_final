from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import dp
from utils.db_api import db_commands

db = db_commands.DBCommands()
buy_callback = CallbackData('buy', 'item_id')


@dp.inline_handler()
async def empty_query(query: types.InlineQuery, state: FSMContext):
    user = query.from_user.id
    allow = await db.check_allow()
    if not allow:
        await query.answer(
            results=[],
            switch_pm_text='Бот недоступен. Подключить бота',
            switch_pm_parameter='connect_user',
            cache_time=5)
        return
    # all_items = await db.show_items()
    all_items = await db.show_sorted_items(query.query or None)

    bot_username = (await query.bot.get_me()).username
    bot_link = 'https://t.me/{bot_username}?start={item_id}'
    articles = [types.InlineQueryResultArticle(
        id=item.id,
        title=item.name,
        description='Цена: {price:,} RUB'.format(price=item.price / 100),
        input_message_content=types.InputTextMessageContent(
            message_text=item.name,
            parse_mode='HTML'
        ),
        thumb_url=item.photo,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Показать товар',
                                     url=bot_link.format(bot_username=bot_username, item_id=item.id))
            ]
        ])
    ) for item in all_items]

    await query.answer(articles, cache_time=5, switch_pm_text='Выберите товар', switch_pm_parameter='select_item')

import datetime
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.deep_linking import get_start_link

from data.config import ADMINS
from keyboards.inline.callbackdata_factory import buy_item
from keyboards.inline.keyboards import keyboard_success_auth, keyboard_start_deep_link, keyboard_admin
from loader import dp
from utils.db_api import db_commands, models


db = db_commands.DBCommands()


# Ловим item_id товара в deep_link с помощью регулярного выражения
@dp.message_handler(CommandStart(deep_link=re.compile(r'i(\d+)')))
async def connect_user(message: types.Message, state: FSMContext):
    args = message.get_args()[1:]
    item: models.Item = await db.get_item(int(args))
    price = item.price / 100

    await state.update_data(
        item=item,
        purchase=models.Purchase(
            buyer=message.from_user.id,
            item_id=item.id,
            purchase_time=datetime.datetime.now(),
        )
    )

    text = f'Название: <b>{item.name}</b>\n\n' \
           f'Описание: <i>{item.description}</i>\n\n' \
           f'Цена: <b>{price:,} RUB</b>\n\n' \
           f'Фотография: {item.photo}\n\n'
    await message.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Купить',
                    callback_data=buy_item.new(item_id=item.id)
                )
            ]
        ]
    ))


# Ловим команду /start, если пользователь пришел по реферальной ссылке или без
@dp.message_handler(CommandStart(deep_link=re.compile(r'u(\d+)')))
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    chat_id = message.from_user.id
    referrer = message.get_args()[1:]
    # referrer = message.get_args()[1:]
    bot_username = (await message.bot.get_me()).username
    referral_id = message.from_user.id
    referral_link = f'https://t.me/{bot_username}?start=u{referral_id}'
    channel_link = 'https://t.me/udemy_final_project'
    allow = await db.check_allow()
    reg_user = await db.check_user()

    if not reg_user:
        await db.add_new_user()

    if allow:
        await message.answer(f'Привет, {message.from_user.full_name}!')
        await message.answer(f'Ваша реферальная ссылка: {referral_link}', reply_markup=keyboard_success_auth)

    elif not referrer or referrer == 'connect_user':
        await message.answer('Чтобы использовать этого бота, введите код приглашения, '
                             'либо пройдите по реферальной ссылке!',
                             reply_markup=keyboard_start_deep_link)
    else:
        await db.set_allow()
        await db.set_ref_link()
        await db.add_money_referral(referrer, '10')

        await message.answer(f'Привет, {message.from_user.full_name}!')
        await message.answer(f'Ваша реферальная ссылка: {referral_link}', reply_markup=keyboard_success_auth)


@dp.callback_query_handler(text='cancel', state='*')
async def cancel_command(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(text='balance')
async def check_balance(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    balance = await db.check_balance()
    await call.message.answer(f'Ваш баланс: {balance} $')


@dp.callback_query_handler(text='referrals')
async def check_balance(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    referrals = await db.check_referrals()
    if len(referrals) > 0:
        await call.message.answer(f'Ваши рефералы: {referrals}')
    else:
        await call.message.answer('У Вас пока нет рефералов.')


@dp.callback_query_handler(text='share_ref_link')
async def share_refferal_link(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    user_id = call.from_user.id
    deep_link = await get_start_link(payload=f'u{user_id}')

    await call.message.answer(f'Ваша реферальная ссылка: {deep_link}')

import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import dp, bot
from states.admin import Invite, Purchase
from data.config import INVITE_CODES, CHANNELS
from utils import photo_link
from utils.db_api import db_commands, models
from keyboards.inline.keyboards import keyboard_success_code, keyboard_start_deep_link, keyboard_subscribe, \
    keyboard_buy_confirm, keyboard_payment
from utils.misc import subscription

db = db_commands.DBCommands()
buy_item = CallbackData('buy', 'item_id')


@dp.message_handler(CommandStart(deep_link='10'))
async def connect_user(message: types.Message, state: FSMContext):
    args = message.get_args()
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


@dp.callback_query_handler(buy_item.filter())
async def enter_quantity(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)

    await call.message.answer('Введите количество товара')
    await Purchase.Quantity.set()


@dp.message_handler(state=Purchase.Quantity)
async def get_quantity(message: types.Message, state: FSMContext):
    quantity = message.text
    try:
        await state.update_data(quantity=int(quantity))
        await message.answer('Укажите адрес доставки')
        await Purchase.Shipping_address.set()
    except ValueError:
        await message.answer('Вы ввели не число! Введите, пожалуйста, число.')


@dp.message_handler(state=Purchase.Shipping_address)
async def get_shipping_address(message: types.Message, state: FSMContext):
    shipping_address = message.text
    await state.update_data(shipping_address=shipping_address)
    data = await state.get_data()
    item: models.Item = data.get('item')
    purchase: models.Purchase = data.get('purchase')
    price = item.price / 100
    quantity = data.get('quantity')
    amount = price * quantity
    await message.answer(f'Вы хотите купить:\n\n'
                         f'Товар: <b>{item.name}</b>\n\n'
                         f'Цена: <b>{price:,} RUB</b>\n\n'
                         f'Количество: <b>{quantity}</b>\n\n'
                         f'Сумма: <b>{amount} RUB</b>\n\n'
                         f'Адрес доставки: <b>{shipping_address}</b>\n\n'
                         f'Подтверждаете?', reply_markup=keyboard_buy_confirm)

    await state.update_data(
        item=item,
        purchase=models.Purchase(
            quantity=quantity,
            amount=amount,
            shipping_address=shipping_address,
        )
    )

    await Purchase.Buying.set()


@dp.callback_query_handler(text_contains='buy_confirm', state=Purchase.Buying)
async def buy_confirm(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)

    data = await state.get_data()
    purchase: models.Purchase = data.get('purchase')
    await purchase.create()
    await state.update_data(purchase=purchase)

    await call.message.edit_reply_markup()
    await call.message.answer('Выберите способ оплаты', reply_markup=keyboard_payment)
    await Purchase.Send_Invoice.set()


@dp.callback_query_handler(text_contains='buy_cancel', state=Purchase.Send_Invoice)
async def buy_confirm(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили покупку.')
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    args = message.get_args()
    print(args)
    chat_id = message.from_user.id
    referral = message.get_args()
    bot_username = (await message.bot.get_me()).username
    referral_id = message.from_user.id
    referral_link = f'https://t.me/{bot_username}?start={referral_id}'
    channel_link = 'https://t.me/udemy_final_project'

    reg_user = await db.check_user()
    if not reg_user:
        await db.add_new_user()

    if not referral or referral == 'connect_user':
        await message.answer('Чтобы использовать этого бота, введите код приглашения, '
                             'либо пройдите по реферальной ссылке!',
                             reply_markup=keyboard_start_deep_link)
    else:
        await db.set_allow()
        await db.add_money_referral(referral, '10')

        await message.answer(f'Привет, {message.from_user.full_name}!')
        await message.answer(f'Ваша реферальная ссылка: {referral_link}')


@dp.callback_query_handler(text='invite_code')
async def enter_invite_code(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.edit_text('Введите код приглашения >>>')
    await Invite.Code.set()


@dp.message_handler(state=Invite.Code)
async def check_invite_code(message: types.Message, state: FSMContext):
    invite_code = message.text

    if invite_code not in INVITE_CODES:
        await message.answer('К сожалению, введенный код неверный! '
                             'Чтобы попробовать еще раз, нажмите /start')
    else:
        await db.set_allow()
        await message.answer('Код введен успешно.', reply_markup=keyboard_success_code)

    await state.reset_state()


@dp.callback_query_handler(text='cancel', state='*')
async def cancel_command(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(text='channel')
async def subscribe_channel(call: types.CallbackQuery):
    await call.answer(cache_time=60)

    await call.message.answer('Чтобы получить реферальную ссылку, '
                              'необходимо подписаться на канал @udemy_final_project',
                              reply_markup=keyboard_subscribe)


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

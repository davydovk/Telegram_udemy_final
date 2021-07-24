import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callbackdata_factory import buy_item
from keyboards.inline.keyboards import keyboard_buy_confirm, keyboard_payment
from loader import dp
from states.admin import Purchase
from utils.db_api import db_commands, models


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
    buyer = message.from_user.id
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
            buyer=buyer,
            item_id=item.id,
            quantity=quantity,
            amount=amount,
            purchase_time=datetime.datetime.now(),
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


@dp.callback_query_handler(text_contains='buy_cancel', state='*')
async def buy_confirm(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили покупку.')
    await call.message.edit_reply_markup()
    await state.reset_state()

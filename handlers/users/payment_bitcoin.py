from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode
from blockcypher import from_satoshis

from data import config
from keyboards.inline.keyboards import paid_btc_keyboard
from loader import dp
from states.admin import Purchase
from utils.db_api import models
from utils.misc.bitcoin_payments import NotConfirmed, NoPaymentFound, Payment
from utils.misc.qr_code import qr_link


@dp.callback_query_handler(text='bitcoin', state=Purchase.Send_Invoice)
async def create_invoice(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)

    data = await state.get_data()
    purchase: models.Purchase = data.get('purchase')
    item: models.Item = data.get('item')

    amount = item.price + randint(5, 500)
    payment = Payment(amount=amount)
    payment.create()

    show_amount = from_satoshis(payment.amount, 'btc')
    await call.message.answer(f'Оплатите {show_amount:.8f} по адресу:\n\n' +
                              hcode(config.WALLET_BTC),
                              reply_markup=paid_btc_keyboard)
    qr_code = config.REQUEST_LINK.format(address=config.WALLET_BTC,
                                         amount=show_amount,
                                         message=item.name)
    await call.message.answer_photo(photo=qr_link(qr_code))
    await Purchase.Payment_BTC.set()
    await state.update_data(payment=payment)


@dp.callback_query_handler(text='cancel_btc', state=Purchase.Payment_BTC)
async def cancel_payment(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.edit_text('Отменено')
    await state.finish()


@dp.callback_query_handler(text='paid_btc', state=Purchase.Payment_BTC)
async def approve_payment(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    payment: Payment = data.get('payment')
    try:
        payment.check_payment()
    except NotConfirmed:
        await call.answer(cache_time=5)
        await call.message.answer('Транзакция найдена. Но еще не подтверждена. Попробуйте позже')
        return
    except NoPaymentFound:
        await call.answer(cache_time=5)
        await call.message.answer('Транзакция не найдена.')
        return
    else:
        await call.message.answer('Успешно оплачено')
    await call.message.delete_reply_markup()
    await state.finish()

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hlink, hcode

from handlers.users.start import db
from keyboards.inline.keyboards import paid_qiwi_keyboard
from loader import dp, bot
from states.admin import Purchase
from utils.db_api import db_commands, models
from utils.misc.qiwi import Payment, NoPaymentFound, NotEnoughMoney


@dp.callback_query_handler(text='qiwi', state=Purchase.Send_Invoice)
async def create_invoice(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    purchase: models.Purchase = data.get('purchase')
    item: models.Item = data.get('item')

    amount = item.price // 100
    payment = Payment(amount=amount)
    payment.create()

    await call.message.answer(
        "\n".join([
            f"Оплатите не менее <b>{amount:.2f} RUB</b> по ссылке ниже:",
            "",
            hlink('Ссылка для оплаты', url=payment.invoice),
            "ID платежа:",
            hcode(payment.id)
        ]),
        reply_markup=paid_qiwi_keyboard)

    await state.set_state(Purchase.Payment_QIWI)
    await state.update_data(payment=payment)


@dp.callback_query_handler(text="cancel", state=Purchase.Payment_QIWI)
async def cancel_payment(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отменено")
    await state.finish()


@dp.callback_query_handler(text="paid", state=Purchase.Payment_QIWI)
async def approve_payment(call: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    item: models.Item = data.get('item')
    purchase: models.Purchase = data.get('purchase')

    item_amount = item.price // 100

    payment: Payment = data.get("payment")

    user_id = call.from_user.id
    user = await db.get_user(user_id)

    try:
        payment.check_payment()
    except NoPaymentFound:
        await call.answer(cache_time=5)
        await call.message.answer("Транзакция не найдена.")
        return
    except NotEnoughMoney:
        await call.message.answer("Оплаченная сума меньше необходимой.")
        return

    else:
        await call.message.answer("Успешно оплачено")
        await purchase.update(
            successful=True
        ).apply()

    await call.message.edit_reply_markup()
    await state.finish()

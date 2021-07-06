from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, ContentType
from aiogram.utils.callback_data import CallbackData
from emoji import emojize

from data.config import PAYMENT_TOKEN
from loader import dp, bot
from states.admin import Purchase
from utils.db_api import db_commands, models

db = db_commands.DBCommands()


@dp.callback_query_handler(text='sberbank', state=Purchase.Send_Invoice)
async def payment(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    purchase: models.Purchase = data.get('purchase')
    item: models.Item = data.get('item')

    currency = "RUB"
    need_name = True
    need_phone_number = False
    need_email = True
    need_shipping_address = False

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.name,
                           description=item.name,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=item.name, amount=item.price * purchase.quantity)
                           ],
                           provider_token=PAYMENT_TOKEN,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address)

    await state.update_data(purchase=purchase)

    await Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=Purchase.Payment)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)
    await bot.send_message(chat_id=pre_checkout_query.from_user.id, text="Спасибо за покупку! Ожидайте отправку")


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=Purchase.Payment)
async def process_successful_payment(message: Message, state: FSMContext):
    total_amount = message.successful_payment.total_amount // 100
    currency = message.successful_payment.currency

    data = await state.get_data()
    purchase: models.Purchase = data.get('purchase')

    await purchase.update(
        successful=True
    ).apply()

    await bot.send_message(message.chat.id, f'Оплата прошла успешно.\nСпасибо за покупку'
                                            f'\nСтоимость покупки = {total_amount} {currency}')

    await state.reset_state()

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hlink, hcode

from keyboards.inline.keyboards import paid_keyboard
from loader import dp, bot
from states.admin import Purchase
from utils.db_api import db_commands, models
from utils.misc.qiwi import Payment, NoPaymentFound, NotEnoughMoney

db = db_commands.DBCommands()

# Используем CallbackData для работы с коллбеками, в данном случае для работы с покупкой товаров
buy_item = CallbackData('buy', 'item_id')


@dp.callback_query_handler(text='bitcoin', state=Purchase.Send_Invoice)
async def create_invoice(call: CallbackQuery, state: FSMContext):
    await call.answer('Извините, оплата с помощью биткоин пока в разработке, выберите другой способ оплаты.',
                      show_alert=True)
    await state.reset_state()

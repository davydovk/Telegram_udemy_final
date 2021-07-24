from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import INVITE_CODES
from handlers.users.start import db
from keyboards.inline.keyboards import keyboard_success_auth
from loader import dp
from states.admin import Invite
from utils.db_api import db_commands


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
        await db.set_invite_code()
        await message.answer('Код введен успешно.', reply_markup=keyboard_success_auth)

    await state.reset_state()

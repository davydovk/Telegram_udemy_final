from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, bot
from states.admin import Invite
from data.config import INVITE_CODES, CHANNELS
from utils import photo_link
from utils.db_api import db_commands
from keyboards.inline.keyboards import keyboard_success_code, keyboard_start_deep_link, keyboard_subscribe
from utils.misc import subscription

db = db_commands.DBCommands()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
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

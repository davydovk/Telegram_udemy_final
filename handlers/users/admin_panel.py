from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from loader import dp, bot
from states.admin import NewItem, Mailing
from utils import photo_link
from utils.db_api.models import Item, User


@dp.message_handler(user_id=ADMINS, commands=['cancel'], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы отменили создание товара')
    await state.reset_state()


@dp.message_handler(user_id=ADMINS, commands=['add_item'])
async def add_item(message: types.Message):
    await message.answer('Введите название товара или нажмите /cancel')
    await NewItem.Name.set()


@dp.message_handler(user_id=ADMINS, state=NewItem.Name)
async def add_name_item(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(f'Название: <b>{name}</b>\n\nПришлите мне описание товара или нажмите /cancel')
    # await message.answer(f'Название: {name}\nПришлите мне цену товара в копейках или нажмите /cancel')

    await NewItem.Desc.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=ADMINS, state=NewItem.Desc)
async def add_description_item(message: types.Message, state: FSMContext):
    desc = message.text
    data = await state.get_data()
    item: Item = data.get('item')
    item.description = desc

    await message.answer(f'Название: <b>{item.name}</b>'
                         f'\n\nПришлите мне фотографию товара (не документ) или нажмите /cancel')

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=ADMINS, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    link = await photo_link(photo)
    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    # await message.answer(link)

    data = await state.get_data()
    item: Item = data.get('item')
    item.photo = link

    await message.answer_photo(
        photo=link,
        caption=('Название: <b>{name}</b>'
                 '\n\nПришлите мне цену товара в копейках или нажмите /cancel').format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=ADMINS, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item')
    try:
        price = int(message.text)
    except ValueError:
        await message.answer('Неверное значение, введите число')
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text='Да', callback_data='confirm')],
            [InlineKeyboardButton(text='Ввести заново', callback_data='change')],
        ]
    )
    await message.answer('Цена: <b>{price:,} RUB</b>\n'
                         'Подтверждаете? Нажмите /cancel чтобы отменить'.format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=ADMINS, text_contains='change', state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer('Введите заново цену товара в копейках')
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=ADMINS, text_contains='confirm', state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get('item')
    await item.create()
    await call.message.answer(f'Товар удачно создан.\n\n'
                              f'Название: <b>{item.name}</b>\n\n'
                              f'Описание: <i>{item.description}</i>\n\n'
                              f'Цена: <b>{item.price} RUB</b>\n\n'
                              f'Фотография: {item.photo}\n\n'
                              f'Если хотите создать еще один товар, нажмите /add_item')
    await state.reset_state()


# Фича для рассылки по юзерам (учитывая их язык)
@dp.message_handler(user_id=ADMINS, commands=['tell_everyone'])
async def mailing(message: types.Message):
    await message.answer('Пришлите текст рассылки')
    await Mailing.Text.set()


@dp.message_handler(user_id=ADMINS, state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text='Русский', callback_data='ru')],
            [InlineKeyboardButton(text='English', callback_data='en')]
        ]
    )
    await message.answer('Пользователям на каком языке разослать это сообщение?\n\n'
                         'Текст:\n'
                         '{text}'.format(text=text),
                         reply_markup=markup)
    await Mailing.Language.set()


@dp.callback_query_handler(user_id=ADMINS, state=Mailing.Language)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')

    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.where(User.language == call.data).gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer('Рассылка выполнена.')

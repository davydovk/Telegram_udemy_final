import asyncio
from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from data.config import ADMINS
from keyboards.inline.keyboards import keyboard_admin, keyboard_set_items
from loader import dp, bot
from states.admin import NewItem, Mailing, EditItem
from utils import photo_link
from utils.db_api import db_commands
from utils.db_api.models import Item, User

db = db_commands.DBCommands()


@dp.message_handler(user_id=ADMINS, commands=['start'])
async def start_admin(message: types.Message):
    await message.answer('Аве, Администратор! Что желаете?', reply_markup=keyboard_admin)


@dp.message_handler(user_id=ADMINS, commands=['cancel'], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы отменили создание товара')
    await state.reset_state()


@dp.callback_query_handler(user_id=ADMINS, text='add_item')
async def add_item(call: types.CallbackQuery):
    await call.answer(cache_time=60)

    await call.message.answer('Введите название товара или нажмите /cancel')
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
                              f'Если хотите вернуться в меню администратора, нажмите /start')
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


'''------------------------------------ДОРАБОТАТЬ---------------------------------------------'''

edit_item = CallbackData('edit', 'item_id', 'action')


@dp.callback_query_handler(user_id=ADMINS, text='set_item')
async def set_item(call: types.CallbackQuery):
    await call.answer(cache_time=60)

    all_items = await db.show_items()
    for item in all_items:
        text = f'Название: <b>{item.name}</b>\n\n' \
               f'Описание: <i>{item.description}</i>\n\n' \
               f'Цена: <b>{item.price:,} RUB</b>\n\n' \
               f'Фотография: {item.photo}\n\n'

        set_item_keyboard = InlineKeyboardMarkup(row_width=1)

        set_name_btn = InlineKeyboardButton(text='Изменить название', callback_data=edit_item.new(item_id=item.id,
                                                                                                  action='name'))
        set_desc_btn = InlineKeyboardButton(text='Изменить описание', callback_data=edit_item.new(item_id=item.id,
                                                                                                  action='desc'))
        set_price_btn = InlineKeyboardButton(text='Изменить цену', callback_data=edit_item.new(item_id=item.id,
                                                                                               action='price'))
        set_photo_btn = InlineKeyboardButton(text='Изменить фотографию', callback_data=edit_item.new(item_id=item.id,
                                                                                                     action='photo'))
        delete_item_btn = InlineKeyboardButton(text='Удалить товар', callback_data=edit_item.new(item_id=item.id,
                                                                                                 action='delete'))

        set_item_keyboard.add(set_name_btn, set_desc_btn, set_price_btn, set_photo_btn, delete_item_btn)

        await call.message.answer(text.format(id=item.id, name=item.name, price=item.price / 100),
                                  reply_markup=set_item_keyboard)
        await asyncio.sleep(0.3)


@dp.callback_query_handler(edit_item.filter(action='name'))
async def edit_item_name(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    item_id = int(callback_data.get('item_id'))
    await call.message.answer('Вы хотите изменить название товара!')
    item = Item.get(item_id)

    if not item:
        await call.message.answer('Такого товара не существует')
        return
    # await db.edit_name_item(item_id, 'new name')
    await call.message.answer('Введите новое название товара.')
    await call.message.edit_reply_markup()
    await EditItem.EditName.set()


@dp.message_handler(user_id=ADMINS, state=EditItem.EditName)
async def enter_new_name(message: types.Message):
    new_item_name = message.text


@dp.inline_handler(user_id=ADMINS)
async def edit_item_query(query: types.InlineQuery):
    all_items = await db.show_sorted_items(query.query or None)

    articles = [types.InlineQueryResultArticle(
        id=item.id,
        title=item.name,
        description='Цена: {price:,} RUB'.format(price=item.price / 100),
        input_message_content=types.InputTextMessageContent(
            message_text='',
            parse_mode='HTML'
        ),
        thumb_url=item.photo,
        # reply_markup=keyboard_set_items
    ) for item in all_items]

    await query.answer(articles, cache_time=5, switch_pm_text='Выберите товар, который хотите изменить',
                       switch_pm_parameter='edit_item')
    await EditItem.EditItem.set()


@dp.message_handler(state=EditItem.EditItem)
async def edit_item_msg(message: types.Message, state: FSMContext):
    text = message.text
    args = message.get_args()
    # item_id = str(text[4:7]).strip()
    # item = await db.get_item(item_id)

    await message.answer(f'text={text}, args={args}')


@dp.callback_query_handler(state=EditItem.EditItem, text='set_name')
async def enter_new_name(call: types.CallbackQuery, state: FSMContext):
    await call.answer('Введите новое имя для товара')

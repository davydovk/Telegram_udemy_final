import re
import datetime
import re
from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data.config import ADMINS
from keyboards.inline.callbackdata_factory import edit_item
from keyboards.inline.keyboards import keyboard_admin, keyboard_set_items, text_language_keyboard, \
    keyboard_set_items_confirm
from loader import dp, bot
from states.admin import NewItem, Mailing, EditItem
from utils import photo_link
from utils.db_api import db_commands, models
from utils.db_api.models import Item, User

db = db_commands.DBCommands()


@dp.message_handler(CommandStart(deep_link=re.compile(r'i(\d+)')), user_id=ADMINS)
async def connect_user(message: types.Message, state: FSMContext):
    args = message.get_args()[1:]
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
                    text='Изменить',
                    callback_data=edit_item.new(item_id=item.id, action='edit')
                )
            ]
        ]
    ))


# Когда команду /start нажимает Администратор
@dp.message_handler(user_id=ADMINS, commands=['start'])
async def start_admin(message: types.Message):
    await message.answer('Аве, Администратор! Что желаете?', reply_markup=keyboard_admin)


@dp.message_handler(user_id=ADMINS, commands=['cancel'], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы отменили создание товара')
    await state.reset_state()


# Создание товара
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
                              f'Цена: <b>{item.price / 100} RUB</b>\n\n'
                              f'Фотография: {item.photo}\n\n'
                              f'Если хотите вернуться в меню администратора, нажмите /start')
    await state.reset_state()


# Изменение товара
@dp.callback_query_handler(edit_item.filter(action='edit'), user_id=ADMINS)
async def set_item(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    item_id = int(callback_data.get('item_id'))
    data = await state.get_data()
    await state.update_data(item_id=item_id)

    await call.message.answer('Что хотите изменить?', reply_markup=keyboard_set_items)


# Изменение названия товара
@dp.callback_query_handler(edit_item.filter(action='edit_name'), user_id=ADMINS)
async def edit_item_name(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item_id = int(data.get('item_id'))
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
async def enter_new_name(message: types.Message, state: FSMContext):
    new_item_name = message.text
    data = await state.get_data()
    item = data.get('item')
    text = f'Старое название: <b>{item.name}</b>\n' \
           f'Новое название: <b>{new_item_name}</b>\n' \
           f'Подтверждаете изменение?'
    await state.update_data(new_item_name=new_item_name)
    await message.answer(text, reply_markup=keyboard_set_items_confirm)


@dp.callback_query_handler(text='confirm_set', user_id=ADMINS, state=EditItem.EditName)
async def edit_name(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    new_item_name = data.get('new_item_name')
    item = data.get('item')
    text = f'Название товара успешно изменено!\n' \
           f'Новое название товара: <b>{new_item_name}</b>'
    await item.update(name=new_item_name).apply()
    await call.message.answer(text)

    await state.reset_state()


@dp.callback_query_handler(text='cancel_set', user_id=ADMINS, state=EditItem.EditName)
async def cancel_edit_name(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили изменение товара')

    await state.reset_state()


# Изменение описания товара
@dp.callback_query_handler(edit_item.filter(action='edit_desc'), user_id=ADMINS)
async def edit_item_desc(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item_id = int(data.get('item_id'))
    await call.message.answer('Вы хотите изменить описание товара!')
    item = Item.get(item_id)

    if not item:
        await call.message.answer('Такого товара не существует')
        return
    # await db.edit_name_item(item_id, 'new name')
    await call.message.answer('Введите новое описание товара.')
    await call.message.edit_reply_markup()
    await EditItem.EditDesc.set()


@dp.message_handler(user_id=ADMINS, state=EditItem.EditDesc)
async def enter_new_desc(message: types.Message, state: FSMContext):
    new_item_desc = message.text
    data = await state.get_data()
    item = data.get('item')
    text = f'Старое описание: <b>{item.description}</b>\n' \
           f'Новое описание: <b>{new_item_desc}</b>\n' \
           f'Подтверждаете изменение?'
    await state.update_data(new_item_desc=new_item_desc)
    await message.answer(text, reply_markup=keyboard_set_items_confirm)


@dp.callback_query_handler(text='confirm_set', user_id=ADMINS, state=EditItem.EditDesc)
async def edit_desc(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    new_item_desc = data.get('new_item_desc')
    item = data.get('item')
    text = f'Описание товара успешно изменено!\n' \
           f'Новое описание товара: <b>{new_item_desc}</b>'
    await item.update(description=new_item_desc).apply()
    await call.message.answer(text)

    await state.reset_state()


@dp.callback_query_handler(text='cancel_set', user_id=ADMINS, state=EditItem.EditDesc)
async def cancel_edit_desc(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили изменение товара')

    await state.reset_state()


# Изменение цены товара
@dp.callback_query_handler(edit_item.filter(action='edit_price'), user_id=ADMINS)
async def edit_item_price(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item_id = int(data.get('item_id'))
    await call.message.answer('Вы хотите изменить цену товара!')
    item = Item.get(item_id)

    if not item:
        await call.message.answer('Такого товара не существует')
        return
    # await db.edit_name_item(item_id, 'new name')
    await call.message.answer('Введите новую цену товара в копейках.')
    await call.message.edit_reply_markup()
    await EditItem.EditPrice.set()


@dp.message_handler(user_id=ADMINS, state=EditItem.EditPrice)
async def enter_new_price(message: types.Message, state: FSMContext):
    try:
        new_item_price = int(message.text)
    except ValueError:
        await message.answer('Неверное значение, введите число')
        return

    data = await state.get_data()
    item = data.get('item')
    text = f'Старая цена: <b>{item.price / 100}</b> RUB\n' \
           f'Новая цена: <b>{new_item_price / 100}</b> RUB\n' \
           f'Подтверждаете изменение?'
    await state.update_data(new_item_price=new_item_price)
    await message.answer(text, reply_markup=keyboard_set_items_confirm)


@dp.callback_query_handler(text='confirm_set', user_id=ADMINS, state=EditItem.EditPrice)
async def edit_price(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    new_item_price = data.get('new_item_price')
    item = data.get('item')
    text = f'Цена товара успешно изменена!\n' \
           f'Новая цена товара: <b>{new_item_price / 100}</b> RUB'
    await item.update(price=new_item_price).apply()
    await call.message.answer(text)

    await state.reset_state()


@dp.callback_query_handler(text='cancel_set', user_id=ADMINS, state=EditItem.EditPrice)
async def cancel_edit_price(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили изменение товара')

    await state.reset_state()


# Изменение фотографии товара
@dp.callback_query_handler(edit_item.filter(action='edit_photo'), user_id=ADMINS)
async def edit_item_photo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item_id = int(data.get('item_id'))
    await call.message.answer('Вы хотите изменить фотографию товара!')
    item = Item.get(item_id)

    if not item:
        await call.message.answer('Такого товара не существует')
        return
    # await db.edit_name_item(item_id, 'new name')
    await call.message.answer('Пришлите мне фотографию товара (не документ)')
    await call.message.edit_reply_markup()
    await EditItem.EditPhoto.set()


@dp.message_handler(user_id=ADMINS, state=EditItem.EditPhoto, content_types=types.ContentType.PHOTO)
async def enter_new_photo(message: types.Message, state: FSMContext):
    new_photo = message.photo[-1]
    new_photo_link = await photo_link(new_photo)
    await message.bot.send_chat_action(message.chat.id, 'upload_photo')

    data = await state.get_data()
    item = data.get('item')
    text = f'Старая фотография: <b>{item.photo}</b>\n' \
           f'Новая фотография: <b>{new_photo_link}</b>\n' \
           f'Подтверждаете изменение?'
    await state.update_data(new_photo_link=new_photo_link)
    await message.answer(text, reply_markup=keyboard_set_items_confirm)


@dp.callback_query_handler(text='confirm_set', user_id=ADMINS, state=EditItem.EditPhoto)
async def edit_photo(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    new_photo_link = data.get('new_photo_link')
    item = data.get('item')
    text = f'Фотография товара успешно изменена!\n' \
           f'Новая фотография товара: <b>{new_photo_link}</b>'
    await item.update(photo=new_photo_link).apply()
    await call.message.answer(text)

    await state.reset_state()


@dp.callback_query_handler(text='cancel_set', user_id=ADMINS, state=EditItem.EditPhoto)
async def cancel_edit_photo(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили изменение товара')

    await state.reset_state()


# Удаление товара
@dp.callback_query_handler(edit_item.filter(action='delete_item'), user_id=ADMINS)
async def delete_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item_id = int(data.get('item_id'))
    item = Item.get(item_id)

    if not item:
        await call.message.answer('Такого товара не существует')
        return

    await call.message.answer('Вы подтверждаете удаление товара?', reply_markup=keyboard_set_items_confirm)
    await EditItem.Delete.set()


@dp.callback_query_handler(text='confirm_set', user_id=ADMINS, state=EditItem.Delete)
async def confirm_delete_item(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    item = data.get('item')
    text = f'Товар <b>{item.name}</b> успешно удален!'
    await item.delete()
    await call.message.answer(text)

    await state.reset_state()


@dp.callback_query_handler(text='cancel_set', user_id=ADMINS, state=EditItem.Delete)
async def cancel_delete_item(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили удаление товара')

    await state.reset_state()


# Создание рассылки по юзерам (учитывая их язык)
@dp.callback_query_handler(user_id=ADMINS, text='tell_everyone')
async def mailing(call: types.CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Пришлите текст рассылки')
    await Mailing.Text.set()


@dp.message_handler(user_id=ADMINS, state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)

    await message.answer('Пользователям на каком языке разослать это сообщение?\n\n'
                         'Текст:\n'
                         '{text}'.format(text=text),
                         reply_markup=text_language_keyboard)

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

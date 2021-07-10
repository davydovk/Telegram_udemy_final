from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


# Клавиатура после успешной авторизации пользователя по коду
keyboard_success_code = InlineKeyboardMarkup(row_width=1)

items_btn = InlineKeyboardButton(text='Товары', switch_inline_query_current_chat='')
balance_btn = InlineKeyboardButton(text='Проверить баланс', callback_data='balance')
referral_btn = InlineKeyboardButton(text='Показать рефералов', callback_data='referrals')
cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel')

keyboard_success_code.add(items_btn, balance_btn, referral_btn, cancel_btn)


# Клавиатура при старте через deep_link
keyboard_start_deep_link = InlineKeyboardMarkup(row_width=1)

code_btn = InlineKeyboardButton(text='Ввести код приглашения', callback_data='invite_code')
channel_btn = InlineKeyboardButton(text='Получить реферальную ссылку', callback_data='channel')

keyboard_start_deep_link.add(code_btn, channel_btn)


# Клавиатура для подписки на канал
channel_link = 'https://t.me/udemy_final_project'

keyboard_subscribe = InlineKeyboardMarkup(row_width=1)

subscribe_btn = InlineKeyboardButton(text='Подписаться на канал', url=channel_link)
check_sub_btn = InlineKeyboardButton(text='Проверить подписку', callback_data='check_subs')
cancel_btn_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel')

keyboard_subscribe.add(subscribe_btn, check_sub_btn, cancel_btn_btn)


# Клавиатура администратора
keyboard_admin = InlineKeyboardMarkup(row_width=1)

add_item_btn = InlineKeyboardButton(text='Создать товар', callback_data='add_item')
set_item_btn = InlineKeyboardButton(text='Изменить товар', callback_data='set_item')
show_items_btn = InlineKeyboardButton(text='Показать все товары', switch_inline_query_current_chat='')
tell_everyone_btn = InlineKeyboardButton(text='Отправить сообщение пользователям', callback_data='tell_everyone')

keyboard_admin.add(add_item_btn, set_item_btn, show_items_btn, tell_everyone_btn)


# Клавиатура для изменения товара
set_item = CallbackData('set', 'item_id', 'action')
keyboard_set_items = InlineKeyboardMarkup(row_width=1)

set_name_btn = InlineKeyboardButton(text='Изменить название', callback_data='set_name')
set_desc_btn = InlineKeyboardButton(text='Изменить описание', callback_data='set_desc')
set_price_btn = InlineKeyboardButton(text='Изменить цену', callback_data='set_price')
set_photo_btn = InlineKeyboardButton(text='Изменить фотографию', callback_data='set_photo')
delete_item_btn = InlineKeyboardButton(text='Удалить товар', callback_data='delete_item')

keyboard_set_items.add(set_name_btn, set_desc_btn, set_price_btn, set_photo_btn, delete_item_btn)


# Клавиатура для подтверждения покупки
keyboard_buy_confirm = InlineKeyboardMarkup(row_width=1)

confirm_btn = InlineKeyboardButton(text='Подтверждаю', callback_data='buy_confirm')
cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='buy_cancel')

keyboard_buy_confirm.add(confirm_btn, cancel_btn)


# Клавиатура с выбором способов оплаты
keyboard_payment = InlineKeyboardMarkup(row_width=1)

sberbank_btn = InlineKeyboardButton(text='Сбербанк', callback_data='sberbank')
qiwi_btn = InlineKeyboardButton(text='Киви', callback_data='qiwi')
bitcoin_btn = InlineKeyboardButton(text='Биткоин', callback_data='bitcoin')

keyboard_payment.add(sberbank_btn, qiwi_btn, bitcoin_btn)


# Клавиатура подтверждения оплаты с помощью QIWI
paid_keyboard = InlineKeyboardMarkup(row_width=1)

paid_btn = InlineKeyboardButton(text="Оплатил", callback_data="paid")
cancel_btn = InlineKeyboardButton(text="Отмена", callback_data="cancel")

paid_keyboard.add(paid_btn, cancel_btn)

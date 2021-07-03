from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize

# Клавиатура после успешной авторизации пользователя по коду
keyboard_success_code = InlineKeyboardMarkup(row_width=1)

items_btn = InlineKeyboardButton(text='Товары', switch_inline_query_current_chat='')
cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel')

keyboard_success_code.add(items_btn, cancel_btn)


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

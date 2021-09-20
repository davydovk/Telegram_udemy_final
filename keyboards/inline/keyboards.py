from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize


# Клавиатура после успешной авторизации
keyboard_success_auth = InlineKeyboardMarkup(row_width=1)

items_btn = InlineKeyboardButton(text=f'{emojize(":shopping_cart:")} Выбрать товар',
                                 switch_inline_query_current_chat='')
balance_btn = InlineKeyboardButton(text=f'{emojize(":money_bag:")} Проверить баланс', callback_data='balance')
referral_btn = InlineKeyboardButton(text=f'{emojize(":busts_in_silhouette:")} Показать рефералов',
                                    callback_data='referrals')
share_ref_link_btn = InlineKeyboardButton(text=f'{emojize(":left_arrow_curving_right:")} Получить реферальную ссылку'
                                          , callback_data='share_ref_link')
cancel_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel')

keyboard_success_auth.add(items_btn, balance_btn, referral_btn, share_ref_link_btn, cancel_btn)


# Клавиатура при старте через deep_link
keyboard_start_deep_link = InlineKeyboardMarkup(row_width=1)

code_btn = InlineKeyboardButton(text=f'{emojize(":slot_machine:")} Ввести код приглашения', callback_data='invite_code')
channel_btn = InlineKeyboardButton(text=f'{emojize(":postbox:")} Получить реферальную ссылку', callback_data='channel')

keyboard_start_deep_link.add(code_btn, channel_btn)


# Клавиатура для подписки на канал
channel_link = 'https://t.me/udemy_final_project'

keyboard_subscribe = InlineKeyboardMarkup(row_width=1)

subscribe_btn = InlineKeyboardButton(text=f'{emojize(":bell:")} Подписаться на канал', url=channel_link)
check_sub_btn = InlineKeyboardButton(text=f'{emojize(":magnifying_glass_tilted_left:")} Проверить подписку',
                                     callback_data='check_subs')
cancel_btn_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel')

keyboard_subscribe.add(subscribe_btn, check_sub_btn, cancel_btn_btn)


# Клавиатура администратора
keyboard_admin = InlineKeyboardMarkup(row_width=1)

add_item_btn = InlineKeyboardButton(text=f'{emojize(":plus:")} Создать товар', callback_data='add_item')
set_item_btn = InlineKeyboardButton(text=f'{emojize(":pencil:")} Изменить товар', callback_data='set_item')
show_items_btn = InlineKeyboardButton(text=f'{emojize(":magnifying_glass_tilted_left:")} Показать все товары',
                                      switch_inline_query_current_chat='')
share_ref_link_btn = InlineKeyboardButton(text=f'{emojize(":left_arrow_curving_right:")} Получить реферальную ссылку'
                                          , callback_data='share_ref_link')
check_referrals_btn = InlineKeyboardButton(text=f'{emojize(":busts_in_silhouette:")} Показать рефералов',
                                           callback_data='referrals')
tell_everyone_btn = InlineKeyboardButton(text=f'{emojize(":envelope:")} Отправить сообщение пользователям',
                                         callback_data='tell_everyone')
check_balance_btn = InlineKeyboardButton(text=f'{emojize(":money_bag:")} Проверить баланс', callback_data='balance')

keyboard_admin.add(add_item_btn, show_items_btn, tell_everyone_btn, check_balance_btn, check_referrals_btn,
                   share_ref_link_btn)


# Клавиатура для изменения товара
keyboard_set_items = InlineKeyboardMarkup(row_width=1)

set_name_btn = InlineKeyboardButton(text=f'{emojize(":pencil:")} Изменить название',
                                    callback_data='set:item_id:edit_name')
set_desc_btn = InlineKeyboardButton(text=f'{emojize(":pencil:")} Изменить описание',
                                    callback_data='set:item_id:edit_desc')
set_price_btn = InlineKeyboardButton(text=f'{emojize(":pencil:")} Изменить цену',
                                     callback_data='set:item_id:edit_price')
set_photo_btn = InlineKeyboardButton(text=f'{emojize(":pencil:")} Изменить фотографию',
                                     callback_data='set:item_id:edit_photo')
delete_item_btn = InlineKeyboardButton(text=f'{emojize(":wastebasket:")} Удалить товар',
                                       callback_data='set:item_id:delete_item')

keyboard_set_items.add(set_name_btn, set_desc_btn, set_price_btn, set_photo_btn, delete_item_btn)


# Клавиатура для подтверждения изменения товара
keyboard_set_items_confirm = InlineKeyboardMarkup(row_width=1)

confirm_set_btn = InlineKeyboardButton(text=f'{emojize(":check_mark_button:")} Подтверждаю',
                                       callback_data='confirm_set')
cancel_set_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel_set')

keyboard_set_items_confirm.add(confirm_set_btn, cancel_set_btn)


# Клавиатура для подтверждения покупки
keyboard_buy_confirm = InlineKeyboardMarkup(row_width=1)

confirm_btn = InlineKeyboardButton(text=f'{emojize(":check_mark_button:")} Подтверждаю', callback_data='buy_confirm')
cancel_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='buy_cancel')

keyboard_buy_confirm.add(confirm_btn, cancel_btn)


# Клавиатура с выбором способов оплаты
keyboard_payment = InlineKeyboardMarkup(row_width=1)

sberbank_btn = InlineKeyboardButton(text=f'{emojize(":bank:")} Сбербанк', callback_data='sberbank')
qiwi_btn = InlineKeyboardButton(text=f'{emojize(":kiwi_fruit:")} Qiwi', callback_data='qiwi')
bitcoin_btn = InlineKeyboardButton(text=f'{emojize(":credit_card:")} Bitcoin', callback_data='bitcoin')
cancel_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel')

keyboard_payment.add(sberbank_btn, qiwi_btn, bitcoin_btn, cancel_btn)


# Клавиатура подтверждения оплаты с помощью QIWI
paid_qiwi_keyboard = InlineKeyboardMarkup(row_width=1)

paid_btn = InlineKeyboardButton(text=f'{emojize(":check_mark_button:")} Оплатил', callback_data='paid')
cancel_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel')

paid_qiwi_keyboard.add(paid_btn, cancel_btn)


# Клавиатура подтверждения оплаты с помощью Bitcoin
paid_btc_keyboard = InlineKeyboardMarkup(row_width=1)

paid_btc_btn = InlineKeyboardButton(text=f'{emojize(":check_mark_button:")} Оплатил', callback_data='paid_btc')
cancel_btc_btn = InlineKeyboardButton(text=f'{emojize(":cross_mark:")} Отмена', callback_data='cancel_btc')

paid_btc_keyboard.add(paid_btc_btn, cancel_btc_btn)


# Клавиатура выбора языка для рассылки сообщений пользователям
text_language_keyboard = InlineKeyboardMarkup(row_width=1)

ru_btn = InlineKeyboardButton(text=f'{emojize(":Russia:")} Русский', callback_data='ru')
en_btn = InlineKeyboardButton(text=f'{emojize(":England:")} English', callback_data='en')

text_language_keyboard.add(ru_btn, en_btn)

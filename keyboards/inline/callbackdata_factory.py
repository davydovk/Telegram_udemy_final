from aiogram.utils.callback_data import CallbackData

buy_item = CallbackData('buy', 'item_id')
edit_item = CallbackData('set', 'item_id', 'action')

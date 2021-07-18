from aiogram.dispatcher.filters.state import StatesGroup, State


class NewItem(StatesGroup):
    Name = State()
    Desc = State()
    Photo = State()
    Price = State()
    Confirm = State()


class EditItem(StatesGroup):
    EditItem = State()
    EditName = State()
    EditDesc = State()
    EditPhoto = State()
    EditPrice = State()


class Mailing(StatesGroup):
    Text = State()
    Language = State()


class Invite(StatesGroup):
    Code = State()


class Purchase(StatesGroup):
    Quantity = State()
    Shipping_address = State()
    Buying = State()
    Send_Invoice = State()
    Payment = State()
    Payment_QIWI = State()
    Payment_BTC = State()

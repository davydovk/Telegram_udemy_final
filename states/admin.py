from aiogram.dispatcher.filters.state import StatesGroup, State


class NewItem(StatesGroup):
    Name = State()
    Desc = State()
    Photo = State()
    Price = State()
    Confirm = State()


class Mailing(StatesGroup):
    Text = State()
    Language = State()


class Invite(StatesGroup):
    Code = State()

import datetime
from typing import List
from aiogram import types, Bot
from asyncpg import Connection
from sqlalchemy import and_

from utils.db_api.models import User, Item, Purchase
from utils.db_api.database import db


class DBCommands:

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name

        if referral:
            new_user.referral = int(referral)
        await new_user.create()
        return new_user

    async def set_language(self, language):
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(language=language).apply()

    async def count_users(self) -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def check_referrals(self):
        bot = Bot.get_current()
        user_id = types.User.get_current().id

        user = await User.query.where(User.user_id == user_id).gino.first()
        referrals = await User.query.where(User.referral == user.id).gino.all()

        return ", ".join([
            f"{num + 1}. " + (await bot.get_chat(referral.user_id)).get_mention(as_html=True)
            for num, referral in enumerate(referrals)
        ])

    async def show_items(self):
        # items = await Item.query.gino.all()
        items = await Item.query.order_by(Item.name).gino.all()

        return items

    async def show_sorted_items(self, search_query: str = None):
        if search_query:
            search_items = await Item.query.where(Item.description.ilike(f'%{search_query}%')).gino.all()
        else:
            search_items = await Item.query.order_by(Item.name).gino.all()

        return search_items

    async def check_balance(self):
        user_id = types.User.get_current().id
        balance = await User.select('balance').where(User.id == int(user_id)).gino.scalar()

        return balance

    async def add_money(self, money):
        user = types.User.get_current()
        balance = await self.check_balance()
        await user.update(balance=balance + int(money)).apply()

    async def add_money_referral(self, referral_id, money):
        user = await User.query.where(User.user_id == int(referral_id)).gino.first()
        balance = user.balance
        await user.update(balance=balance + int(money)).apply()

    async def check_allow(self):
        user_id = types.User.get_current().id
        allow = await User.select('allow').where(User.user_id == user_id).gino.scalar()
        if allow:
            print('Вход разрешен')
            return True
        else:
            print('Вход не разрешен')
            return False

    async def set_allow(self):
        user_id = types.User.get_current().id
        user = await User.query.where(User.user_id == user_id).gino.first()
        allow = user.allow
        await user.update(allow=True).apply()

    async def check_user(self):
        user_id = types.User.get_current().id
        user = await User.query.where(User.user_id == user_id).gino.first()
        if user:
            return True
        else:
            return False

    async def edit_name_item(self, item_id, name):
        item = await Item.query.where(Item.id == item_id).gino.first()
        await item.update(name=name).apply()

    async def get_item(self, item_id):
        item = await Item.query.where(Item.id == int(item_id)).gino.first()

        return item


# Функция для создания нового товара в базе данных. Принимает все возможные аргументы, прописанные в Item
async def add_item(**kwargs):
    new_item = await Item(**kwargs).create()
    return new_item

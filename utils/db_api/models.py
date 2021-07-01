from sqlalchemy import (Column, Integer, String, Sequence, BigInteger, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql
from utils.db_api.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    language = Column(String(2))
    full_name = Column(String(100))
    username = Column(String(50))
    balance = Column(Integer, default=0)
    referral = Column(Integer)
    allow = Column(Boolean, default=False)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Item(db.Model):
    __tablename__ = 'items'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    description = Column(String(4096))
    photo = Column(String(250))
    price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Item(id='{}', name='{}', description='{}', photo='{}', price='{}')>".format(
            self.id, self.name, self.description, self.photo, self.price)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    item_id = Column(Integer)
    amount = Column(Integer)  # Цена в копейках (потом делим на 100)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

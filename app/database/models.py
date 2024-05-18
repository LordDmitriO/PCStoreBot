from sqlalchemy import BigInteger, ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List

from config import ENGINE, ECHO

engine = create_async_engine(ENGINE)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


"""
админ (айдиб тг_айди)
юзер (айди, тг_айди)
категория (айди, имя)
товар (айди, имя, описание, картинка, цена, категория)
корзина (айди, айди_юзера, айди_товара)
"""
class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] =  mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True)

    basket_rel: Mapped[List['Basket']] = relationship(back_populates='user_rel')
    order_rel: Mapped[List['Order']] = relationship(back_populates='user_rel')

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    subcategory_rel: Mapped[List['Subcategory']] = relationship(back_populates='category_rel')
    item_rel: Mapped[List['Item']] = relationship(back_populates='category_rel')


class Subcategory(Base):
    __tablename__ = 'subcategories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category_rel: Mapped[List['Category']] = relationship(back_populates='subcategory_rel')
    item_rel: Mapped[List['Item']] = relationship(back_populates='subcategory_rel')


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(3000))
    photo: Mapped[str] = mapped_column(String(200))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    subcategory: Mapped[int] = mapped_column(ForeignKey('subcategories.id'))

    category_rel: Mapped['Category'] = relationship(back_populates='item_rel')
    subcategory_rel: Mapped['Subcategory'] = relationship(back_populates='item_rel')
    basket_rel: Mapped[List['Basket']] = relationship(back_populates='item_rel')
    order_rel: Mapped[List['Order']] = relationship(back_populates='item_rel')

class Promotion(Base):
    __tablename__ = 'promotions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(3000))
    date_start: Mapped[str] = mapped_column(String(20))
    date_end: Mapped[str] = mapped_column(String(20))


class Basket(Base):
    __tablename__ = 'basket'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))

    user_rel: Mapped['User'] = relationship(back_populates='basket_rel')
    item_rel: Mapped['Item'] = relationship(back_populates='basket_rel')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[int] = mapped_column()
    user = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    name: Mapped[str] =  mapped_column(String(100))
    number: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(100), nullable=True)
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))
    status: Mapped[str] = mapped_column(String(20))

    user_rel: Mapped['User'] = relationship(back_populates='order_rel')
    item_rel: Mapped['Item'] = relationship(back_populates='order_rel')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

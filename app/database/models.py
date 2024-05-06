from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List

from config import ENGINE, ECHO

engine = create_async_engine(ENGINE)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


"""
юзер (айди, тг_айди)
категория (айди, имя)
товар (айди, имя, описание, картинка, цена, категория)
корзина (айди, айди_юзера, айди_товара)
"""
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] =  mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

    basket_rel: Mapped[List['Basket']] = relationship(back_populates='user_rel')


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    subcategory_rel: Mapped[List['Subcategory']] = relationship(back_populates='category_rel')


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
    description: Mapped[str] = mapped_column(String(300))
    photo: Mapped[str] = mapped_column(String(200))
    price: Mapped[int] = mapped_column()
    subcategory: Mapped[int] = mapped_column(ForeignKey('subcategories.id'))

    subcategory_rel: Mapped['Subcategory'] = relationship(back_populates='item_rel')
    basket_rel: Mapped[List['Basket']] = relationship(back_populates='item_rel')


class Basket(Base):
    __tablename__ = 'basket'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))

    user_rel: Mapped['User'] = relationship(back_populates='basket_rel')
    item_rel: Mapped['Item'] = relationship(back_populates='basket_rel')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

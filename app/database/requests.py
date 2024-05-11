from app.database.models import Admin, User, Category, Subcategory, Item, Basket, Promotion
from app.database.models import async_session

from sqlalchemy import select, update, delete


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def set_item(data):
    async with async_session() as session:
        session.add(Item(**data))
        await session.commit()


async def set_basket(tg_id, item_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Basket(user=user.id, item=item_id))
        await session.commit()


async def get_basket(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        basket = await session.scalars(select(Basket).where(Basket.user == user.id))
        return basket


async def get_admins():
    async with async_session() as session:
        admins = await session.scalars(select(Admin.tg_id))
        return admins


async def get_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users
    

async def get_promotions():
    async with async_session() as session:
        promotions = await session.scalars(select(Promotion))
        return promotions
    

async def get_promotion_by_id(promotion_id: int):
    async with async_session() as session:
        promotion = await session.scalar(select(Promotion).where(Promotion.id == promotion_id))
        return promotion


async def get_categories():
    async with async_session() as session:
        categories = await session.scalars(select(Category))
        return categories
    

async def get_subcategories_by_category(category_id: int):
    async with async_session() as session:
        subcategories = await session.scalars(select(Subcategory).where(Subcategory.category == category_id))
        return subcategories
    

async def get_items_by_subcategory(subcategory_id: int):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(Item.subcategory == subcategory_id))
        return items
    

async def get_item_by_id(item_id: int):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        return item
    

async def delete_basket(tg_id, item_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        await session.execute(delete(Basket).where(Basket.user == user.id, Basket.item == item_id))
        await session.commit()

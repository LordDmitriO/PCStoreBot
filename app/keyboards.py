from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_promotions, get_categories, get_subcategories_by_category, get_items_by_subcategory


main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📖Каталог📖', 
                                                                   callback_data='catalog')],
                                             [InlineKeyboardButton(text='🛒Корзина🛒', 
                                                                   callback_data='mybasket'),
                                              InlineKeyboardButton(text='🧳Заказы🧳',
                                                                   callback_data='myorders')],
                                             [InlineKeyboardButton(text='ℹ️О насℹ️',
                                                                   callback_data='about'),
                                              InlineKeyboardButton(text='☎️Контакты☎️', 
                                                                   callback_data='contacts')],
                                             [InlineKeyboardButton(text='💰Акции💰', 
                                                                   callback_data='promotions')]])

to_main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main')]])


async def delete_from_basket_go_to_total(order_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='❌Удалить из корзины❌', callback_data=f'delete_{order_id}'))
    keyboard.add(InlineKeyboardButton(text='📦Перейти к оформлению📦', callback_data='total'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def basket(order_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✋Добавить в корзину✋', callback_data=f'order_{order_id}'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def making_order():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✋Самовывоз✋', callback_data='pickup'))
    keyboard.add(InlineKeyboardButton(text='🚚Курьер🚚', callback_data='delivery'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def pay():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='💳Оплатить💳', callback_data='pay'))
    return keyboard.adjust(1).as_markup()


async def ready_order():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def about():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def contacts():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def promotions():
    all_promotions = await get_promotions()
    keyboard = InlineKeyboardBuilder()
    for promotion in all_promotions:
        keyboard.add(InlineKeyboardButton(text=promotion.name,
                                          callback_data=f'promotion_{promotion.id}'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, 
                                          callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def subcategories(category_id: int):
    all_subcategories = await get_subcategories_by_category(category_id)
    keyboard = InlineKeyboardBuilder()
    for subcategory in all_subcategories:
        keyboard.add(InlineKeyboardButton(text=subcategory.name, 
                                          callback_data=f'subcategory_{subcategory.id}'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def items(subcategory_id: int):
    items = await get_items_by_subcategory(subcategory_id)
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.add(InlineKeyboardButton(text=item.name,
                                          callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='🏠На главную🏠', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

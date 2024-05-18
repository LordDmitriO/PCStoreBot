from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from app.database.requests import get_admins, get_users, set_item, set_promotion


admin = Router()


class Newsletter(StatesGroup):
    message = State()
    # confirm = State()


class AddItem(StatesGroup):
    name = State()
    category = State()
    subcategory = State()
    description = State()
    photo = State()
    price = State()


class AddPromotion(StatesGroup):
    name = State()
    description = State()
    date_start = State()
    date_end = State()


class AdminProtect(Filter):
    async def __call__(self, message: Message):
        admins = []
        for admin in await get_admins():
            admins.append(admin)
        return message.from_user.id in admins


@admin.message(AdminProtect(), Command('adminpanel'))
async def adminpanel(message: Message):
    await message.answer('Возможные команды:\n/newsletter\n/add_item\n/add_promotion')


@admin.message(AdminProtect(), Command('newsletter'))
async def newslettter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Отправьте сообщение, которое вы хотите разослать всем пользователям.')


@admin.message(AdminProtect(), Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    await message.answer('Подождите... идет рассылка.')
    for user in await get_users():
        try:
            await message.send_copy(chat_id=user.tg_id)
        except:
            pass
    await message.answer('Рассылка успешно завершена.')
    await state.clear()

"""
    name = State()
    category = State()
    subcategory = State()
    description = State()
    photo = State()
    price = State()
"""
@admin.message(AdminProtect(), Command('add_item'))
async def add_item(message: Message, state: FSMContext):
    await state.set_state(AddItem.name)
    await message.answer('Введите название товара.')


@admin.message(AdminProtect(), AddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddItem.category)
    await message.answer('Выберите категорию товара.', reply_markup=await kb.categories())


@admin.callback_query(AdminProtect(), AddItem.category)
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=int(callback.data.split('_')[1]))
    await state.set_state(AddItem.subcategory)
    await callback.answer('')
    await callback.message.answer('Выберите подкатегорию товара.', reply_markup=await kb.subcategories(category_id=int(callback.data.split('_')[1])))


@admin.callback_query(AdminProtect(), AddItem.subcategory)
async def add_item_subcategory(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory=int(callback.data.split('_')[1]))
    await state.set_state(AddItem.description)
    await callback.answer('')
    await callback.message.answer('Введите описание товара.')


@admin.message(AdminProtect(), AddItem.description)
async def add_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddItem.photo)
    await message.answer('Отправьте фото товара.')


@admin.message(AdminProtect(), AddItem.photo, F.photo)
async def add_item_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AddItem.price)
    await message.answer('Введите цену товара.')


@admin.message(AdminProtect(), AddItem.price)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text))
    data = await state.get_data()
    await set_item(data)
    await message.answer('Товар успешно добавлен.')
    await state.clear()


@admin.message(AdminProtect(), Command('add_promotion'))
async def add_promotion(message: Message, state: FSMContext):
    await state.set_state(AddPromotion.name)
    await message.answer('Введите название акции.')


@admin.message(AdminProtect(), AddPromotion.name)
async def add_promotion_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddPromotion.description)
    await message.answer('Введите описание акции.')


@admin.message(AdminProtect(), AddPromotion.description)
async def add_promotion_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddPromotion.date_start)
    await message.answer('Введите дату начала акции.')


@admin.message(AdminProtect(), AddPromotion.date_start)
async def add_promotion_date_start(message: Message, state: FSMContext):
    await state.update_data(date_start=message.text)
    await state.set_state(AddPromotion.date_end)
    await message.answer('Введите дату окончания акции.')


@admin.message(AdminProtect(), AddPromotion.date_end)
async def add_promotion_date_end(message: Message, state: FSMContext):
    await state.update_data(date_end=message.text)
    data = await state.get_data()
    await set_promotion(data)
    await message.answer('Акция успешно добавлена.')
    await state.clear()




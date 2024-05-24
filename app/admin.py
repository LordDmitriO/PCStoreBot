from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from app.database.requests import get_admins, get_users, set_item, set_promotion, delete_item, delete_promotion


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


class DeleteItem(StatesGroup):
    name = State()
    price = State()
    category = State()
    subcategory = State()


class DeletePromotion(StatesGroup):
    id = State()


class AdminProtect(Filter):
    async def __call__(self, message: Message):
        admins = []
        for admin in await get_admins():
            admins.append(admin)
        return message.from_user.id in admins


@admin.message(AdminProtect(), Command('adminpanel'))
async def adminpanel(message: Message):
    await message.answer('Добро пожаловать в панель администратора.\nВозможные команды:\n\n/newsletter - разослать пользователям сообщение'
                         '\n\nДобавление:\n/add_item - добавить новый товар\n/add_promotion - добавить новую акцию' 
                         '\n\nУдаление:\n/delete_item - удалить существующий товар\n/delete_promotion - удалить существующую акцию')


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


@admin.message(AdminProtect(), Command('delete_item'))
async def input_delete_item(message: Message, state: FSMContext):
    await state.set_state(DeleteItem.name)
    await message.answer('Введите название товара.')


@admin.message(AdminProtect(), DeleteItem.name)
async def delete_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(DeleteItem.price)
    await message.answer('Введите цену товара.')


@admin.message(AdminProtect(), DeleteItem.price)
async def delete_item_price(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text))
    await state.set_state(DeleteItem.category)
    await message.answer('Выберите категорию товара.', reply_markup=await kb.categories())


@admin.callback_query(AdminProtect(), DeleteItem.category)
async def delete_item_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=int(callback.data.split('_')[1]))
    await state.set_state(DeleteItem.subcategory)
    await callback.answer('')
    await callback.message.answer('Выберите подкатегорию товара.', reply_markup=await kb.subcategories(category_id=int(callback.data.split('_')[1])))


@admin.callback_query(AdminProtect(), DeleteItem.subcategory)
async def delete_item_subcategory(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory=int(callback.data.split('_')[1]))
    data = await state.get_data()
    await delete_item(data)
    await callback.message.answer('Товар успешно удален.')
    await state.clear()


@admin.message(AdminProtect(), Command('delete_promotion'))
async def input_delete_promotion(message: Message, state: FSMContext):
    await state.set_state(DeletePromotion.id)
    await message.answer('Выберите акцию, которую вы хотите удалить.', reply_markup=await kb.promotions())


@admin.callback_query(AdminProtect(), DeletePromotion.id)
async def delete_promotion_date_end(callback: CallbackQuery, state: FSMContext):
    await state.update_data(id=int(callback.data.split('_')[1]))
    data = await state.get_data()
    await delete_promotion(data)
    await callback.message.answer('Акция успешно удалена.')
    await state.clear()

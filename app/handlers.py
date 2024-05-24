from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from app.database.requests import (get_promotion_by_id, get_item_by_id, set_user, set_basket, set_order, 
                                   get_basket, get_item_in_basket, get_orders, get_order_by_id, delete_item_in_basket, delete_basket)
from app.functions import o_number


router = Router()


class Reg_pickup(StatesGroup):
    name = State()
    number = State()

class Reg_delivery(StatesGroup):
    name = State()
    number = State()
    address = State()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await set_user(message.from_user.id)
        await message.answer('Добро пожаловать в интернет-магазин комплектующих для ПК 🖥PCStore🖥!',
                            reply_markup=kb.main)
    else:
        await message.answer('Вы вернулись на главную.')
        await message.message.answer('Добро пожаловать в интернет-магазин комплектующих для ПК 🖥PCStore🖥!',
                            reply_markup=kb.main)
        

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы находитесь на странице помощи для пользователей бота!\n\nЧтобы начать пользоваться ботом вызовите команду /start')
    

@router.callback_query(F.data == 'about')
async def about(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('👋 Добро пожаловать в наш магазин компьютерных комплектующих! 🖥️\n\n'
                                     'Мы - команда энтузиастов, которые любят технологии и стремятся делиться своими знаниями с нашими клиентами.\n\n'
                                     '🌟 Наша цель - сделать ваше путешествие по миру компьютерных компонентов легким, удобным и вдохновляющим.'
                                     'Мы предлагаем широкий ассортимент качественных продуктов, чтобы помочь вам создать идеальную систему для ваших потребностей и желаний. \n\n'
                                     '🛠️ С нами вы можете быть уверены в качестве и надежности каждого товара, который вы приобретаете. Мы следим за последними трендами и технологическими новинками, чтобы предложить вам самое лучшее.\n\n'
                                     '🤝 Мы стремимся к удовлетворению наших клиентов и готовы ответить на любые ваши вопросы, поделиться советами и предложить индивидуальные решения под ваши потребности.\n\n'
                                     'Спасибо, что выбрали нас!',
                                     reply_markup=await kb.contacts())


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите категорию.', 
                         reply_markup=await kb.categories())
    

@router.callback_query(F.data == 'contacts')
async def contacts(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Наши контакты:\nПочта: otvalnyui@otval.com\nТелефон: +7(228)775-47-82\nАдрес: Отвальная улица д.228 к.478, вход со стороны подвала.',
                                     reply_markup=await kb.contacts())
    

@router.callback_query(F.data == 'promotions')
async def promotions(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите интересующую вас акцию из списка:',
                                     reply_markup=await kb.promotions())
    

@router.callback_query(F.data.startswith('promotion_'))
async def promotion(callback: CallbackQuery):
    promotion_id = int(callback.data.split('_')[1])
    promotion = await get_promotion_by_id(promotion_id)
    await callback.answer('')
    await callback.message.edit_text(text=f'{promotion.name}\n\n{promotion.description}\n\nДата начала: {promotion.date_start}\nДата окончания: {promotion.date_end}',
                                     reply_markup=kb.to_main)


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.message.edit_text('Выберите подкатегорию.',
                                  reply_markup=await kb.subcategories(int(callback.data.split('_')[1])))
    

@router.callback_query(F.data.startswith('subcategory_'))
async def subcategory(callback: CallbackQuery):
    await callback.message.edit_text('Выберите товар.',
                                  reply_markup=await kb.items(int(callback.data.split('_')[1])))
    

@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item_id = int(callback.data.split('_')[1])
    item = await get_item_by_id(item_id)
    await callback.answer('')
    await callback.message.answer_photo(photo=item.photo, caption=f'{item.name}\n\n{item.description}\n\nЦена: {item.price} рублей',
                                  reply_markup=await kb.basket(item.id))
    

@router.callback_query(F.data.startswith('order_'))
async def basket(callback: CallbackQuery):
    await set_basket(callback.from_user.id, int(callback.data.split('_')[1]))
    await callback.answer('Товар добавлен в корзину.')


@router.callback_query(F.data == 'mybasket')
async def mybasket(callback: CallbackQuery):
    await callback.answer('')
    basket = await get_basket(callback.from_user.id)
    counter = 0
    for item_info in basket:
        item = await get_item_by_id(item_info.item)
        await callback.message.answer_photo(photo=item.photo, caption=f'{item.name}\n\n{item.description}\n\nЦена: {item.price} рублей',
                                            reply_markup=await kb.delete_from_basket_go_to_total(item.id))
        counter += 1
    await callback.message.answer('Ваша корзина пуста.') if counter == 0 else await callback.answer('')


@router.callback_query(F.data == 'myorders')
async def myorders(callback: CallbackQuery):
    await callback.answer('')
    orders = await get_orders(callback.from_user.id)
    counter = 0
    items_data = {}
    pieces_data = {}
    numbers = []
    for order_info in orders:
        order = await get_order_by_id(order_info.id)
        item = await get_item_by_id(order_info.item)
        if (item.name in items_data) and (item.name in pieces_data):
            items_data[item.name] += int(item.price)
            pieces_data[item.name] += 1
        else:
            items_data[item.name] = int(item.price)
            pieces_data[item.name] = 1

        items = []
        items.append(f'Номер заказа - {order.order_number}\n\nКонтактная информация:\nИмя: {order.name}\nТелефон: {order.number}\nАдрес: {order.address}\n\nСостав заказа:\n')
        number = 0
        for name, price in items_data.items():
            number += 1             
            items.append(f'{number}. {name}: {price} рублей - {pieces_data[name]} шт')

        items.append(f'\nОбщая сумма заказа: {sum(items_data.values())} рублей\n\nСтатус заказа - {order.status}')
        await callback.message.answer('\n'.join(items), reply_markup=kb.to_main)
        counter += 1
        items_data = {}
        pieces_data = {}
    await callback.message.answer('У вас нет заказов.') if counter == 0 else await callback.answer('')


@router.callback_query(F.data == 'total')
async def total(callback: CallbackQuery):
    my_items = await get_basket(callback.from_user.id)
    items_data = {}
    pieces_data = {}
    for myitem in my_items:
        item = await get_item_by_id(myitem.item)
        if (item.name in items_data) and (item.name in pieces_data):
            items_data[item.name] += int(item.price)
            pieces_data[item.name] += 1
        else:
            items_data[item.name] = int(item.price)
            pieces_data[item.name] = 1

    items = []
    items.append(f'Проверьте ваш заказ:\n')
    number = 0
    for name, price in items_data.items():
        number += 1
        items.append(f'{number}. {name}: {price} рублей - {pieces_data[name]} шт')
    
    items.append(f'\nОбщая сумма: {sum(items_data.values())} рублей\n\nВыберите способ доставки:')
    await callback.message.answer('\n'.join(items), reply_markup=await kb.making_order())


@router.callback_query(F.data == 'pickup')
async def reg_pickup_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg_pickup.name)
    await callback.message.answer('Введите свое имя')


@router.message(Reg_pickup.name)
async def reg_pickup_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg_pickup.number)
    await message.answer('Введите свой номер телефона')


@router.message(Reg_pickup.number)
async def reg_pickup_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await state.update_data(order_number=o_number)
    await state.update_data(user=message.from_user.id)
    for item_get in await get_item_in_basket(message.from_user.id):
        await state.update_data(item=item_get)
    await state.update_data(status='Обработка')
    data = await state.get_data()
    await set_order(data)
    await message.answer(f'Проверьте свою информацию:\n\nИмя: {data['name']}\nНомер: {data['number']}', reply_markup=await kb.pay())
    await state.clear()


@router.callback_query(F.data == 'delivery')
async def reg_delivery_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg_delivery.name)
    await callback.message.answer('Введите свое имя')


@router.message(Reg_delivery.name)
async def reg_delivery_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg_delivery.number)
    await message.answer('Введите свой номер телефона')


@router.message(Reg_delivery.number)
async def reg_delivery_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await state.set_state(Reg_delivery.address)
    await message.answer('Введите свой адрес')


@router.message(Reg_delivery.address)
async def reg_delivery_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.update_data(order_number=o_number)
    await state.update_data(user=message.from_user.id)
    for item_get in await get_item_in_basket(message.from_user.id):
        await state.update_data(item=item_get)
        await state.update_data(status='Обработка')
        data = await state.get_data()
        await set_order(data)
    await message.answer(f'Проверьте свою информацию:\n\nИмя: {data['name']}\nНомер: {data['number']}\nАдрес: {data['address']}', reply_markup=await kb.pay())
    await state.clear()


@router.callback_query(F.data == 'pay')
async def ready_pay(callback: CallbackQuery):
    await callback.answer('')
    await delete_basket(callback.from_user.id)
    await callback.message.edit_text(f'Заказ успешно оплачен!\n\nВаш номер заказа - {o_number}\n\nВ ближайшее время с вами свяжется менеджер для уточнения деталей заказа.',
                                     reply_markup=await kb.ready_order())

        
@router.callback_query(F.data.startswith('delete_'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_item_in_basket(callback.from_user.id, int(callback.data.split('_')[1]))
    await callback.message.delete()
    await callback.answer('Вы удалили товар из корзины')

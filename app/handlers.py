from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keyboards as kb
from app.database.requests import get_promotion_by_id, get_item_by_id, set_user, set_basket, get_basket, delete_basket


router = Router()


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
                                            reply_markup=await kb.delete_from_basket(item.id))
        counter += 1
    await callback.message.answer('Ваша корзина пуста.') if counter == 0 else await callback.answer('')
        

@router.callback_query(F.data.startswith('delete_'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_basket(callback.from_user.id, int(callback.data.split('_')[1]))
    await callback.message.delete()
    await callback.answer('Вы удалили товар из корзины')

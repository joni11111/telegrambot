import logging

import dotenv
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards import create_inline_keyboard
import app.keyboards as kb
import app.datebase.requests as rq
from dotenv import *
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
TG_ID = os.getenv('ADMIN_TG_ID')
# Укажите свой Telegram ID
ADMIN_TG_ID = TG_ID # Замените на ваш Telegram ID

# Инициализация роутера
router = Router()

# Состояния для FSM
class OrderState(StatesGroup):
    waiting_for_category = State()
    waiting_for_item = State()
    waiting_for_location = State()

# Обработчик команды /start
@router.message(CommandStart())
async def start_command(message: Message):
    await rq.set_user(message.from_user.id)  # Сохраняем пользователя в базе данных
    await message.answer(
        "Добро пожаловать! Вы можете сделать заказ, выбрав категорию.",
        reply_markup=kb.main  # Кнопка "Заказать"
    )

# Обработчик для команды "Заказать"
@router.message(Command(commands=["order"]))  # Если команда - /order
async def order_command(message: types.Message):
    categories_markup = await kb.categories()  # Получаем клавиатуру с категориями
    await message.answer("Выберите категорию для заказа:", reply_markup=categories_markup)

# Регистрация команды "Заказать" как текстовой команды
@router.message(lambda message: message.text and message.text.lower() == "заказать")  # Если пользователь пишет "Заказать"
async def handle_order_text_command(message: types.Message):
    await order_command(message)

# Обработчик выбора категории (CallbackQuery)
@router.callback_query(F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    items_markup = await kb.items(category_id)  # Получаем товары по категории

    # Сохраняем выбранную категорию в FSM-состояние
    await state.update_data(category_id=category_id)
    await callback.message.edit_text("Выберите товар:", reply_markup=items_markup)

# Измененный обработчик выбора товара
@router.callback_query(lambda cb: cb.data.startswith("item_"))
async def item_selected(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[1])
    item = await rq.get_item(item_id)  # Получаем информацию о товаре из базы данных

    if item is None:
        await callback.answer("Товар не найден.")
        return

    # Получаем текущий список товаров или создаем новый
    data = await state.get_data()
    selected_items = data.get("selected_items", [])  # Используем список для хранения товаров
    selected_items.append(item)  # Добавляем новый выбранный товар в список

    # Обновляем состояние с новым списком товаров
    await state.update_data(selected_items=selected_items)

    # Отправляем информацию о товаре с клавиатурой
    keyboard = create_inline_keyboard()  # Используем функцию для создания клавиатуры
    await callback.message.edit_text(
        f"Вы выбрали {item.name}. Цена: {item.price} KZT. Описание: {item.description}",
        reply_markup=keyboard
    )


# Обработчик кнопки "Хочу заказать ещё"
@router.callback_query(lambda cb: cb.data == "order_more")
async def order_more_callback(callback: CallbackQuery):
    # Отправляем клавиатуру с категориями для нового заказа
    categories_markup = await kb.categories()
    await callback.message.answer("Выберите категорию для нового заказа:", reply_markup=categories_markup)


# Измененный обработчик завершения заказа
@router.callback_query(lambda cb: cb.data == "button2")
async def complete_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, отправьте ваше местоположение (например, кабинет 208, главный корпус, 87053793834).")
    await state.set_state(OrderState.waiting_for_location)  # Устанавливаем состояние ожидания местоположения

# Обработчик получения текстового местоположения
@router.message(StateFilter(OrderState.waiting_for_location))
async def location_received(message: Message, state: FSMContext):
    user_location = message.text
    logger.info(f"Получено местоположение: {user_location}")

    # Получаем данные о заказе из FSM-состояния
    data = await state.get_data()
    selected_items = data.get("selected_items", [])

    # Проверяем, выбраны ли товары
    if selected_items:
        items_info = "\n".join([f"{item.name} - {item.price} KZT" for item in selected_items])
    else:
        items_info = "Информация о товаре отсутствует"

    # Подтверждаем получение заказа и очищаем состояние
    await message.answer('Ваш заказ принят! Ожидайте доставки.')
    await state.clear()

    # Отправляем данные о заказе и местоположении администратору
    await message.bot.send_message(
        ADMIN_TG_ID,
        f"Новый заказ от пользователя @{message.from_user.username or message.from_user.id}:\n"
        f"Товары:\n{items_info}\n"
        f"Местоположение: {user_location}"
    )


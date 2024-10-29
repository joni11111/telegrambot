from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.datebase.requests import get_categories, get_category_item


# Основная кнопка "Заказать"
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Заказать')]
    ],
    resize_keyboard=True
)

def create_inline_keyboard():
    # Создаем список с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Хочу выбрать еще...", callback_data="order_more"),
            InlineKeyboardButton(text="Завершить заказ...", callback_data="button2")
        ]
    ])
    return keyboard

# Клавиатура с категориями
async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))

    # Возвращаем клавиатуру без проверки наличия атрибута inline_keyboard
    return keyboard.adjust(2).as_markup()

# Клавиатура с товарами
async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=f"{item.name} - {item.price} KZT", callback_data=f"item_{item.id}"))
    return keyboard.adjust(2).as_markup()

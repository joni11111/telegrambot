from app.datebase.models import async_session, User, Category, Item
from sqlalchemy import select

# Сохранение пользователя
async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

# Получение категорий
async def get_categories():
    async with async_session() as session:
        result = await session.scalars(select(Category))
        categories = list(result)
        print("Категории:", categories)  # Печать для отладки
        return categories



# Получение товаров по категории
async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).filter(Item.category == category_id))

# Получение информации о товаре
async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from workout_api.configs.settings import settings

# Cria a conexão com o banco de dados PostgreSQL
# senha do postgres = alexis
DATABASE_URL = "postgresql://workout:workout@localhost/workout"
engine = create_async_engine(settings.DB_URL, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session

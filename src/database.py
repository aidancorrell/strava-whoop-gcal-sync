from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    from src.models import Base
    import sqlite3

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Add missing columns to existing tables (poor man's migration)
        from sqlalchemy import text
        result = await conn.execute(text("PRAGMA table_info(sync_records)"))
        columns = {row[1] for row in result.fetchall()}
        if "activity_start" not in columns:
            await conn.execute(text("ALTER TABLE sync_records ADD COLUMN activity_start DATETIME"))
        if "activity_end" not in columns:
            await conn.execute(text("ALTER TABLE sync_records ADD COLUMN activity_end DATETIME"))

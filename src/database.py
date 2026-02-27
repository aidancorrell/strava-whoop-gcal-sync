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
        def add_columns_if_missing(sync_conn):
            raw = sync_conn.connection.dbapi_connection
            cursor = raw.cursor()
            columns = {row[1] for row in cursor.execute("PRAGMA table_info(sync_records)")}
            if "activity_start" not in columns:
                cursor.execute("ALTER TABLE sync_records ADD COLUMN activity_start DATETIME")
            if "activity_end" not in columns:
                cursor.execute("ALTER TABLE sync_records ADD COLUMN activity_end DATETIME")

        await conn.run_sync(add_columns_if_missing)

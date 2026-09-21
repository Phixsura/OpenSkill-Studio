from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    # Statement timeout: kill queries running longer than 30s
    # connect_args already sets command_timeout=30
    connect_args={"timeout": 10, "command_timeout": 30},
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    # NOTE: Add pool event listeners for monitoring in production:
    # from sqlalchemy import event
    # event.listen(engine.sync_engine, "checkout", on_checkout)
    # event.listen(engine.sync_engine, "checkin", on_checkin)
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """FastAPI dependency: one session per request."""
    async with AsyncSessionLocal() as session:
        yield session

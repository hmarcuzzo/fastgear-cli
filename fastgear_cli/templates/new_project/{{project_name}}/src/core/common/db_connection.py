from fastgear.common.database.sqlalchemy.session import AsyncDatabaseSessionFactory
from fastgear.decorators import DBSessionDecorator
from pydantic_core import MultiHostUrl

from src.config.settings import settings


def get_database_url() -> str:
    return MultiHostUrl.build(
        scheme=settings.DATABASE_CONNECTION,
        username=settings.DATABASE_USERNAME,
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        path=settings.DATABASE_NAME,
    ).__str__()


async_session_factory = AsyncDatabaseSessionFactory(get_database_url())
db_session_decorator = DBSessionDecorator(async_session_factory)

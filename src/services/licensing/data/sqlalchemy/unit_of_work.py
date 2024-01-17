from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from services.licensing.exceptions import DuplicateEntryException
from services.licensing.data.unit_of_work import TransactionManager


import urllib
from services.licensing.json import custom_json_dumps


def postgres_dsn(
    host: str, port: str, user: str, password: str, db_name: str, ssl: bool = False
) -> str:
    return (
        f"postgresql+asyncpg://{user}:{urllib.parse.quote(password)}"
        f"@{host}:{port}"
        f"/{db_name}"
        f"{'?sslmode=require' if ssl else ''}"
    )


class TransactionManagerImpl(TransactionManager):
    def __init__(self, db_uri: str, implicit_commit: bool = False):
        self._implicit_commit = implicit_commit
        self._engine = create_async_engine(
            db_uri,
            echo=False,
            json_serializer=custom_json_dumps,
            connect_args={"server_settings": {"jit": "off"}},
        )
        self._sessionmaker = sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )
        self._session = None

    async def __aenter__(self):
        self._session = self._sessionmaker()
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            if self._implicit_commit:
                await self.commit()
        await self._session.close()

    @property
    def session(self):
        return self._session

    @property
    def engine(self):
        return self._engine

    async def commit(self):
        try:
            await self._session.commit()
        except IntegrityError:  # we are 'abstracting' the sqlalchemy exception here
            raise DuplicateEntryException

    async def rollback(self):
        await self._session.rollback()

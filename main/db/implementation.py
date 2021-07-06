import os
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.schema import CreateTable

from .table import *

class DataBase():

    _instance: Optional['DataBase'] = None
    _engine: Optional[AsyncEngine] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._engine = create_async_engine("sqlite+aiosqlite:///database.db")
            cls._instance = super().__new__(DataBase)
        return cls._instance

    def __init__(self):
        pass

    async def create_table(self):
        await Base.metadata.create_all(self._engine)

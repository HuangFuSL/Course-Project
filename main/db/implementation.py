import os
import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert

from .table import *
from .error import *
from .utils import *

class DataBase():

    _instance: Optional['DataBase'] = None
    _engine: Optional[AsyncEngine] = None
    _need_create: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._need_create = not os.path.exists('database.db')
            cls._engine = create_async_engine("sqlite+aiosqlite:///data/database.db")
            cls.session = sessionmaker(cls._engine, class_=AsyncSession, expire_on_commit=False)
            cls._instance = super().__new__(DataBase)
        return cls._instance

    def __init__(self):
        pass

    async def create_table(self):
        if self._engine is None:
            raise NotImplementedError
        if self._need_create:
            async with self._engine.begin() as g:
                await g.run_sync(Base.metadata.create_all)
            self._need_create = False

    async def add_house_record(self, records: List[Dict[str, Any]]):
        if self._engine is None:
            raise NotImplementedError
        fixed, volatile = split_records(records, FIXED_FIELDS, VOLATILE_FIELDS)
        for _ in volatile:
            _['date'] = datetime.date.today()
        for _ in fixed:
            _['listing_time'] = datetime.date.fromtimestamp(_['listing_time'])
            _['last_trade_time'] = datetime.date.fromtimestamp(_['last_trade_time'])

        async with self._engine.connect() as c:
            await c.execute(insert(Fixed, values=fixed).prefix_with("OR IGNORE"))
            await c.execute(insert(Volatile, values=volatile))
            await c.commit()

import os
import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import except_
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import text

from .table import *
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

    @staticmethod
    def get_today():
        tz_info = datetime.timezone(datetime.timedelta(hours=8))
        current = datetime.datetime.now()
        return current.astimezone(tz_info).date()

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
            _['date'] = self.get_today()
        for _ in fixed:
            _['listing_time'] = datetime.date.fromtimestamp(_['listing_time'])
            _['last_trade_time'] = datetime.date.fromtimestamp(_['last_trade_time'])

        async with self._engine.connect() as c:
            await c.execute(insert(Fixed, values=fixed).prefix_with("OR IGNORE"))
            await c.execute(insert(Volatile, values=volatile).prefix_with("OR REPLACE"))
            await c.commit()

    async def get_heatmap_data(self):
        pass

    async def get_retrieval_data(self):
        pass

    async def get_regression_data(self):
        pass

    async def query_cities(self):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(select(Fixed.city).group_by(Fixed.city))
            return [_['city'] for _ in cursor.fetchall()]

    async def query_unknown_community(self, city: str):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(except_(
                select(Fixed.community_name).where(Fixed.city == city),
                select(CommunityInfo.community_name)
            ).limit(20))
            return [_['community_name'] for _ in cursor.fetchall()]

    async def add_community_record(self, records: List[Dict[str, Any]]):
        if self._engine is None:
            raise NotImplementedError

        for _ in records:
            _['subway'] = [i.__dict__ for i in _['subway']]
            _['subway'] = add_field(_['subway'], {'community_name': _['community_name']})
        subway, other = extract_field(records, 'subway')
        subway = flatten(subway)

        async with self._engine.connect() as c:
            await c.execute(insert(CommunityInfo, values=other).prefix_with("OR IGNORE"))
            await c.execute(insert(SubwayInfo, values=subway).prefix_with("OR IGNORE"))
            await c.commit()

    async def execute(self, command: str):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(text(command))
            return cursor.fetchall()

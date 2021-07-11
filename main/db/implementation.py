import os
import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from sqlalchemy import except_
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.sql import functions

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

    async def get_heatmap_data_1(self):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                (CommunityInfo.num_on_sale).label("count"),
                CommunityInfo.lng,
                CommunityInfo.lat
            ))
            return cursor.fetchall()

    async def get_heatmap_data_2(self):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                (functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID)).label("count"),
                CommunityInfo.lng,
                CommunityInfo.lat
            ).where(and_(
                Volatile.beike_ID == Fixed.beike_ID,
                Fixed.community_name == CommunityInfo.community_name
            )).group_by(CommunityInfo.lng, CommunityInfo.lat))
            return cursor.fetchall()

    async def get_retrieval_data(self, retrieval_dict: Dict[str, Any]):  # 一次只给20条数据
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                Fixed.beike_ID,
                Volatile.title,
                Volatile.price_per_square * Fixed.outer_square,
                Fixed.outer_square,
                Volatile.price_per_square,
                SubwayInfo.distance,
                Fixed.bedroom,
                Fixed.living_room,
                Fixed.bathroom,
                Fixed.floor_no,
                Fixed.listing_time,
                Fixed.last_trade_time,
                Fixed.decoration
            ).where(and_(
                Fixed.beike_ID == Volatile.beike_ID,
                CommunityInfo.community_name == Fixed.community_name,
                SubwayInfo.community_name == Fixed.community_name,
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'],
                Fixed.property_right == retrieval_dict['property_right'],
                Fixed.mortgage_info == retrieval_dict['mortgage_info']
            )))
            return cursor.fetchall()

    async def get_regression_data(self):
        pass

    async def get_graph_1_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                Volatile.date,
                Volatile.price_per_square
            ).where(and_(
                Fixed.beike_ID == Volatile.beike_ID,
                CommunityInfo.community_name == Fixed.community_name,
                SubwayInfo.community_name == Fixed.community_name,
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'],
                Fixed.property_right == retrieval_dict['property_right'],
                Fixed.mortgage_info == retrieval_dict['mortgage_info']
            )))
            return cursor.fetchall()

    async def get_graph_2_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.count(Fixed.beike_ID),
                Fixed.city
            ).where(and_(
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.city
            ))
            return cursor.fetchall()

    async def get_graph_3_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID),
                Fixed.city
            ).where(and_(
                Fixed.beike_ID == Volatile.beike_ID,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.city
            ))
            return cursor.fetchall()

    async def get_graph_4_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.count(Fixed.beike_ID),
                CommunityInfo.district
            ).where(and_(
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(CommunityInfo.district
            ))
            return cursor.fetchall()

    async def get_graph_5_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID),
                CommunityInfo.district
            ).where(and_(
                Fixed.beike_ID == Volatile.beike_ID,
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(CommunityInfo.district
            ))
            return cursor.fetchall()

    async def get_graph_6_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.count(Fixed.beike_ID),
                SubwayInfo.distance
            ).where(and_(
                Fixed.community_name == SubwayInfo.community_name,
                Fixed.city == retrieval_dict['city'],
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'],
                Fixed.property_right == retrieval_dict['property_right'],
                Fixed.mortgage_info == retrieval_dict['mortgage_info']
            )).group_by(SubwayInfo.distance))
            return cursor.fetchall()

    async def get_graph_7_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID),
                SubwayInfo.distance
            ).where(and_(
                Fixed.community_name == SubwayInfo.community_name,
                Fixed.beike_ID == Volatile.beike_ID,
                Fixed.city == retrieval_dict['city'],
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'],
                Fixed.property_right == retrieval_dict['property_right'],
                Fixed.mortgage_info == retrieval_dict['mortgage_info']
            )).group_by(SubwayInfo.distance))
            return cursor.fetchall()

    async def get_graph_8_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.count(Fixed.beike_ID),
                Fixed.construct_time
            ).where(and_(
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.construct_time))
            return cursor.fetchall()

    async def get_graph_9_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID),
                Fixed.construct_time
            ).where(and_(
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.beike_ID == Volatile.beike_ID,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.construct_time))
            return cursor.fetchall()

    async def get_graph_10_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.count(Fixed.beike_ID),
                Fixed.outer_square
            ).where(and_(
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.outer_square))
            return cursor.fetchall()

    async def get_graph_11_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                functions.sum(Volatile.price_per_square) / functions.count(Volatile.beike_ID),
                Fixed.outer_square
            ).where(and_(
                Fixed.city == retrieval_dict['city'],
                CommunityInfo.district == retrieval_dict['area'],
                CommunityInfo.street == retrieval_dict['street'],
                Fixed.community_name == CommunityInfo.community_name,
                Fixed.beike_ID == Volatile.beike_ID,
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'])
            ).group_by(Fixed.outer_square))
            return cursor.fetchall()

    async def get_graph_12_data(self, retrieval_dict: Dict[str, Any]):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select(
                CommunityInfo.lng,
                CommunityInfo.lat
            ).where(and_(
                CommunityInfo.community_name == Fixed.community_name,
                Fixed.city == retrieval_dict['city'],
                Fixed.bedroom >= retrieval_dict['bedroom_min'],
                Fixed.bedroom <= retrieval_dict['bedroom_max'],
                Fixed.living_room >= retrieval_dict['living_room_min'],
                Fixed.living_room <= retrieval_dict['living_room_max'],
                Fixed.bathroom >= retrieval_dict['bathroom_min'],
                Fixed.bathroom <= retrieval_dict['bathroom_max'],
                Fixed.outer_square >= retrieval_dict['outer_square_min'],
                Fixed.outer_square <= retrieval_dict['outer_square_max'],
                Fixed.inner_square >= retrieval_dict['inner_square_min'],
                Fixed.inner_square <= retrieval_dict['inner_square_max'],
                Fixed.elevator_ratio >= retrieval_dict['elevator_ratio_min'],
                Fixed.elevator_ratio <= retrieval_dict['elevator_ratio_max'],
                Fixed.construct_time >= retrieval_dict['house_life_min'],
                Fixed.construct_time <= retrieval_dict['house_life_max'],
                Fixed.property_right == retrieval_dict['property_right'],
                Fixed.mortgage_info == retrieval_dict['mortgage_info']
            )))
            return cursor.fetchall()

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

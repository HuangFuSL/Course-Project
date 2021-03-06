import os
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from sqlalchemy import except_
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import or_
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
            _['date'] = get_today()
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
            cursor = await c.execute(select([
                (CommunityInfo.num_on_sale).label("count"),
                CommunityInfo.lng,
                CommunityInfo.lat
            ]))
            return cursor.fetchall()

    async def get_heatmap_data_2(self):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select([
                (func.sum(Volatile.price_per_square) /
                 func.count(Volatile.beike_ID)).label("count"),
                CommunityInfo.lng,
                CommunityInfo.lat
            ]).where(and_(
                Volatile.beike_ID == Fixed.beike_ID,
                Fixed.community_name == CommunityInfo.community_name
            )).group_by(CommunityInfo.lng, CommunityInfo.lat))
            return cursor.fetchall()

    def build_criteria(self, criteria: Dict[str, Any], restrict_time: bool = True):
        ret = [
            Volatile.date == select([func.max(Volatile.date)]). \
                group_by(Volatile.date).                        \
                scalar_subquery()
        ] if restrict_time else False
        candidate = {
            'city': lambda _: Fixed.city == _['city'],
            'area': lambda _: CommunityInfo.district == _['area'],
            'bedroom_min': lambda _: Fixed.bedroom >= _['bedroom_min'],
            'bedroom_max': lambda _: Fixed.bedroom <= _['bedroom_max'],
            'living_room_min': lambda _: Fixed.living_room >= _['living_room_min'],
            'living_room_max': lambda _: Fixed.living_room <= criteria['living_room_max'],
            'bathroom_min': lambda _: Fixed.bathroom >= _['bathroom_min'],
            'bathroom_max': lambda _: Fixed.bathroom <= _['bathroom_max'],
            'floor': lambda _: Fixed.floor_no == _['floor'],
            'house_life_min': lambda _: Fixed.construct_time >= _['house_life_min'],
            'house_life_max': lambda _: Fixed.construct_time <= _['house_life_max'],
            'outer_square_min': lambda _: Fixed.outer_square >= _['outer_square_min'],
            'outer_square_max': lambda _: Fixed.outer_square <= _['outer_square_max'],
            'decoration': lambda _: Fixed.property_right == _['decoration'],
        }

        if criteria.get('location', None) is not None:
            lat1, lat2 = calc_lat_range(**criteria['location'])
            lng1, lng2 = calc_lng_range(**criteria['location'])

            if lng1 < lng2:
                lng = and_(
                    CommunityInfo.lng >= lng1,
                    CommunityInfo.lng <= lng2
                )
            else:
                lng = or_(
                    CommunityInfo.lng >= lng1,
                    CommunityInfo.lng <= lng2
                )

            ret.extend([
                CommunityInfo.lat >= lat1,
                CommunityInfo.lat <= lat2,
                lng
            ])

        if criteria.get('last_trade_time', None) is not None:
            trade_time_candidate = [
                # '?????????': 0,
                # '?????????': 1,
                # '????????????': 2,
                Fixed.last_trade_time <= get_years_ago(5),
                and_(
                    Fixed.last_trade_time > get_years_ago(5),
                    Fixed.last_trade_time <= get_years_ago(2),
                ),
                Fixed.last_trade_time > get_years_ago(2),
            ]
            ret.append(trade_time_candidate[criteria['last_trade_time']])
        
        if criteria.get('construct_time', None) is not None:
            construct_time_candidate = [
                and_(
                    Fixed.construct_time <= get_years_ago(_).year,
                    Fixed.construct_time > get_years_ago(_ + 5).year
                )
                for _ in range(5)
            ]
            ret.extend(construct_time_candidate[criteria['construct_time']])

        ret.extend(v(criteria) for k, v in candidate.items() if criteria.get(k, None) is not None)
        ret.extend([
            Fixed.beike_ID > 0,
            Volatile.beike_ID > 0,
            Fixed.construct_time > 0,
            Fixed.beike_ID == Volatile.beike_ID,
            CommunityInfo.city == Fixed.city,
            CommunityInfo.community_name == Fixed.community_name,
            SubwayInfo.community_name == Fixed.community_name,
        ])

        return and_(*ret)

    # ????????????20?????????
    async def get_retrieval_data(self,
        offset: int, limit: int, 
        retrieval_dict: Dict[str, Any]
    ):
        if self._engine is None:
            raise NotImplementedError
        async with self._engine.connect() as c:
            cursor = await c.execute(select([
                Fixed.beike_ID,
                Fixed.city,
                CommunityInfo.district,
                CommunityInfo.street,
                Volatile.title,
                Volatile.price_per_square * Fixed.outer_square,
                Fixed.outer_square,
                Volatile.price_per_square,
                SubwayInfo.distance,
                Fixed.bedroom,
                Fixed.living_room,
                Fixed.bathroom,
                Fixed.floor_no,
                Fixed.construct_time,
                Fixed.last_trade_time,
                Fixed.decoration
            ]).where(self.build_criteria(retrieval_dict)).offset(offset).limit(limit))
            return cursor.fetchall()

    async def get_regression_data(self):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(select([
                Fixed.beike_ID,
                Volatile.price_per_square,
                Fixed.construct_time,
                CommunityInfo.district.label('area'),
                CommunityInfo.street,
                Fixed.community_name,
                Fixed.outer_square,
                Fixed.structure,
                Fixed.construction_type,
                Fixed.direction,
                Fixed.construction_struct,
                Fixed.decoration,
                Fixed.elevator_ratio,
                Fixed.heating,
                Fixed.whether_elevator,
                Fixed.trade_property_right,
                Fixed.mortgage_info,
                Fixed.bedroom,
                Fixed.living_room,
                Fixed.bathroom,
                Fixed.floor_no
            ]).where(self.build_criteria({})))
            return cursor.mappings().fetchall()

    async def get_subway_data(self):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(select([SubwayInfo]))
            return cursor.mappings().fetchall()

    async def get_graph_data(self,
        grouper,
        aggregator: str,
        *args,
        restrict_time: bool = True,
        **criteria: Any
    ):
        if self._engine is None:
            raise NotImplementedError

        if aggregator == 'avg':
            aggregate_val = [
                func.sum(Volatile.price_per_square).label('sum'),
                func.count(Volatile.price_per_square).label('count')
            ]
        elif aggregator == 'count':
            aggregate_val = [func.count(grouper).label('sum')]
        else:
            raise ValueError("Aggregator should be 'avg' or 'count'.")
        
        async with self._engine.connect() as c:
            cursor = await c.execute(
                select([grouper, *aggregate_val]).
                where(self.build_criteria(criteria, restrict_time)).
                group_by(grouper)
            )
            return cursor.fetchall()


    async def query_cities(self):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(select([Fixed.city]).group_by(Fixed.city))
            return [_['city'] for _ in cursor.fetchall()]

    async def query_unknown_community(self, city: str):
        if self._engine is None:
            raise NotImplementedError

        async with self._engine.connect() as c:
            cursor = await c.execute(except_(
                select([Fixed.community_name]).where(Fixed.city == city),
                select([CommunityInfo.community_name])
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

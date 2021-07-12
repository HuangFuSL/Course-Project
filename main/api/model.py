from typing import Optional, List
from pydantic import BaseModel


class HouseRecord(BaseModel):
    title: str
    city: str
    price_per_square: int
    construct_time: int
    community_name: str
    area: str
    street: str
    beike_ID: int
    outer_square: float
    structure: int
    inner_square: Optional[float] = None
    construction_type: int
    direction: int
    construction_struct: int
    decoration: int
    elevator_ratio: float
    heating: int
    whether_elevator: int
    listing_time: float
    trade_property_right: int
    last_trade_time: float
    house_usage: int
    property_right: int
    mortgage_info: int
    bedroom: int
    living_room: int
    bathroom: int
    floor_no: int


class HouseRequest(BaseModel):
    content: List[HouseRecord]
    count: int


class SubwayRecord(BaseModel):
    station_name: str
    distance: int


class CommunityRecord(BaseModel):
    city: str
    community_name: str
    num_on_sale: int
    district: str
    street: str
    subway: Optional[List[SubwayRecord]] = None
    lng: float
    lat: float


class CommunityRequest(BaseModel):
    count: int
    content: List[CommunityRecord]


class Heat_map(BaseModel):
    city: float


class LocationRange(BaseModel):
    lng: float
    lat: float
    dist: int

class Retrieval(BaseModel):
    city: Optional[str] = None                  # 城市
    area: Optional[str] = None                  # 区划
    bedroom_min: Optional[int] = None           # 室数最小值
    bedroom_max: Optional[int] = None           # 室数最大值
    living_room_min: Optional[int] = None       # 厅数最小值
    living_room_max: Optional[int] = None       # 厅数最大值
    bathroom_min: Optional[int] = None          # 卫数最小值
    bathroom_max: Optional[int] = None          # 卫数最大值
    floor: Optional[int] = None                 # 楼层
    house_life_min: Optional[int] = None        # 楼龄最小值
    house_life_max: Optional[int] = None        # 楼龄最大值
    last_trade_time: Optional[int] = None       # 交易年限
    outer_square_min: Optional[float] = None    # 面积最小值
    outer_square_max: Optional[float] = None    # 面积最大值
    decoration: Optional[int] = None            # 装修情况

    location: Optional[LocationRange] = None    # 位置


class Request(BaseModel):
    criteria: Retrieval
    offset: int = 0
    limit: int = 20


class Regression_model(BaseModel):
    current_date: float  # 时间戳

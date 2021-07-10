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


class Retrieval(BaseModel):
    city: Optional[str] = None
    area: Optional[str] = None
    street: Optional[str] = None
    bedroom_min: Optional[int] = None
    bedroom_max: Optional[int] = None
    living_room_min: Optional[int] = None
    living_room_max: Optional[int] = None
    bathroom_min: Optional[int] = None
    bathroom_max: Optional[int] = None
    outer_square_min: Optional[float] = None
    outer_square_max: Optional[float] = None
    inner_square_min: Optional[float] = None
    inner_square_max: Optional[float] = None
    elevator_ratio_min: Optional[float] = None
    elevator_ratio_max: Optional[float] = None
    house_life_min: Optional[int] = None
    house_life_max: Optional[int] = None
    property_right: Optional[int] = None
    mortgage_info: Optional[int] = None


class Regression_model(BaseModel):
    current_date: float  # 时间戳

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
    city: str
    area: str
    street: str
    bedroom_min: int
    bedroom_max: int
    living_room_min: int
    living_room_max: int
    bathroom_min: int
    bathroom_max: int
    outer_square_min: float
    outer_square_max: float
    inner_square_min: Optional[float] = None
    inner_square_max: Optional[float] = None
    elevator_ratio_min: float
    elevator_ratio_max: float
    house_life_min: int
    house_life_max: int
    property_right: int
    mortgage_info: int


class Regression_model(BaseModel):
    current_date: float  # 时间戳

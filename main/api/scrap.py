from ..db import DataBase
from .model import *
from ..model import *
from .utils import *


async def add_house(item: HouseRequest):
    ModelResult().clear()
    await DataBase().add_house_record([_.__dict__ for _ in item.content])
    return wrap_response(len(item.content))


async def query_cities():
    resp = await DataBase().query_cities()
    return wrap_response(resp)

async def query_community(city: str):
    resp = await DataBase().query_unknown_community(city)
    return wrap_response(resp)


async def add_community(item: CommunityRequest):
    ModelResult().clear()
    await DataBase().add_community_record([_.__dict__ for _ in item.content])
    return wrap_response(len(item.content))

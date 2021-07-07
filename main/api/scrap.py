from ..db import DataBase
from ..model import *
from .utils import *


async def add_house(item: HouseRequest):
    await DataBase().add_house_record([_.__dict__ for _ in item.content])
    return wrap_response(len(item.content))


async def query_community():
    resp = await DataBase().query_unknown_community()
    return wrap_response(resp)


async def add_community(item: CommunityRequest):
    await DataBase().add_community_record([_.__dict__ for _ in item.content])
    return wrap_response(len(item.content))

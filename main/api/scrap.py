from ..db import DataBase
from ..model import *



async def add_house(item: HousePostFormat):
    await DataBase().add_house_record([_.__dict__ for _ in item.content])
    return {'code': 0}

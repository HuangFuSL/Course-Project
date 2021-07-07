from ..db import DataBase
from ..model import *

async def heat_map():
    data = await DataBase().get_heatmap_data()
    return {
        'code': 0,
        'msg': '',
        'data': data
    }


async def retrieval(item: Retrieval):
    data = await DataBase().get_retrieval_data()
    return {
        'code': 0,
        'msg': '',
        'data': data
    }


async def regression_model(item: Regression_model):
    data = await DataBase().get_regression_data()
    return {
        'code': 0,
        'msg': '',
        'data': data
    }
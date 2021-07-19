from main.model import ModelResult
from ..db import *
from .model import *
from .utils import wrap_response

async def heat_map_1():
    data = await DataBase().get_heatmap_data_1()
    return wrap_response(data)

async def heat_map_2():
    data = await DataBase().get_heatmap_data_2()
    return wrap_response(data)

def parse_retrieval_arg(item: Retrieval):
    ret = vars(item)
    if ret['location'] is not None:
        ret['location'] = vars(ret['location'])
    return ret

async def retrieval(item: Request):
    offset, limit = item.offset, item.limit
    data = await DataBase().get_retrieval_data(
        offset, limit, parse_retrieval_arg(item.criteria)
    )
    return wrap_response(data)

async def graph_1(item: Retrieval):
    data = await DataBase().get_graph_data(
        Volatile.date,
        'avg', 'price', restrict_time=False,
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_2(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.city,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_3(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.city,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)


async def graph_4(item: Retrieval):
    data = await DataBase().get_graph_data(
        CommunityInfo.district,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_5(item: Retrieval):
    data = await DataBase().get_graph_data(
        CommunityInfo.district,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_6(item: Retrieval):
    data = await DataBase().get_graph_data(
        SubwayInfo.distance,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_7(item: Retrieval):
    data = await DataBase().get_graph_data(
        SubwayInfo.distance,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_8(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.construct_time,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_9(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.construct_time,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_10(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.outer_square,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)

async def graph_11(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.outer_square,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    return wrap_response(data)


async def graph_12(item: Retrieval):
    data = await DataBase().get_distribution(parse_retrieval_arg(item))
    return wrap_response(data)

async def regression_model(param: List[int]):
    return wrap_response(await ModelResult().run(param))


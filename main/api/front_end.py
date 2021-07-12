from ..db import *
from .model import *

async def heat_map_1():
    data = await DataBase().get_heatmap_data_1()
    """
    数量热力图
    返回的样例数据
    [{"count": 6, "lng": 116.612326, "lat": 39.92220205},
    {"count": 22, "lng": 116.3307066, "lat": 40.07476902}]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def heat_map_2():
    data = await DataBase().get_heatmap_data_2()
    """
    价格热力图
    返回的样例数据
    [{"count": 6, "lng": 116.612326, "lat": 39.92220205},
    {"count": 22, "lng": 116.3307066, "lat": 40.07476902}]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

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
    """
    传入参数见model.py
    返回的样例数据（只取前20条）
    <tr onclick="window.open('https://bj.ke.com/ershoufang/101112085073.html');">    这部分只用返回贝壳ID，完整链接可以通过贝壳ID推出来
      <td height="30">苹果南区 观花园大两居 满五年唯一 客厅面宽4.4米
	  </td>
      <td align="right">10000000</td>
      <td align="right">200000</td>
      <td>500米以内</td>
      <td align="center">一室一厅一卫</td>
      <td align="center">低</td>
      <td align="center">5-10年</td>
      <td align="center">未满两年</td>
      <td align="center">50平方米</td>
      <td align="center">精装</td>
    </tr>
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_1(item: Retrieval):
    data = await DataBase().get_graph_data(
        Volatile.date,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    均价-时间走势图
    返回的样例数据
    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']           日期
    [150, 230, 224, 218, 135, 147, 260]                         日期对应的均价 
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_2(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.city,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    """
    数量-城市分布图
    返回的样例数据
    [
                {value: 40, name: 'city 1'},
                {value: 33, name: 'city 2'},
                {value: 28, name: 'city 3'}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_3(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.city,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    均价-城市分布图
    返回的样例数据
    [
                {value: 40, name: 'city 1'},
                {value: 33, name: 'city 2'},
                {value: 28, name: 'city 3'}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }


async def graph_4(item: Retrieval):
    data = await DataBase().get_graph_data(
        CommunityInfo.district,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    """
    数量-区划分布图
    返回的样例数据
    [
                {value: 40, name: '朝阳区'},
                {value: 33, name: '海淀区'},
                {value: 28, name: '西城区'}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_5(item: Retrieval):
    data = await DataBase().get_graph_data(
        CommunityInfo.district,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    均价-区划分布图
    返回的样例数据
    [
                {value: 40, name: '朝阳区'},
                {value: 33, name: '海淀区'},
                {value: 28, name: '西城区'}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_6(item: Retrieval):
    data = await DataBase().get_graph_data(
        SubwayInfo.distance,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    """
    房屋数量-地铁距离分布图
    返回的样例数据
    [
                {value: 40},  距离地铁站距离在0-500米的房屋的数量
                {value: 33},  距离地铁站距离在500-800米的房屋的数量
                {value: 28},  距离地铁站距离在800-1200米的房屋的数量
                {value: 21}   距离地铁站距离在1200米以上的房屋的数量
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_7(item: Retrieval):
    data = await DataBase().get_graph_data(
        SubwayInfo.distance,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    房屋均价-地铁距离分布图
    返回的样例数据
    [
                {value: 40},  距离地铁站距离在0-500米的房屋的均价
                {value: 33},  距离地铁站距离在500-800米的房屋的均价
                {value: 28},  距离地铁站距离在800-1200米的房屋的均价
                {value: 21}   距离地铁站距离在1200米以上的房屋的均价
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_8(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.construct_time,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    """
    房屋数量-楼龄分布图
    返回的样例数据
    [
                {value: 40, age: 10},
                {value: 33, age: 29},
                {value: 28, age: 37}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_9(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.construct_time,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    房屋均价-楼龄分布图
    返回的样例数据
    [
                {value: 40, age: 10},
                {value: 33, age: 29},
                {value: 28, age: 37}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_10(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.outer_square,
        'count', 'count',
        **parse_retrieval_arg(item)
    )
    """
    房屋数量-面积分布图
    返回的样例数据
    [
                {value: 40, area: 10},
                {value: 33, area: 29},
                {value: 28, area: 37}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_11(item: Retrieval):
    data = await DataBase().get_graph_data(
        Fixed.outer_square,
        'avg', 'price',
        **parse_retrieval_arg(item)
    )
    """
    房屋均价-面积分布图
    返回的样例数据
    [
                {value: 40, area: 10},
                {value: 33, area: 29},
                {value: 28, area: 37}
    ]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def graph_12(item: Retrieval):
    data = await DataBase().get_distribution(parse_retrieval_arg(item))
    """
    房屋地理分布图
    返回的样例数据
    [{"lng": 116.612326, "lat": 39.92220205},
     {"lng": 116.3307066, "lat": 40.07476902}]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }

async def regression_model(item: Regression_model):
    retrieval_dict = vars(item)
    data = await DataBase().get_retrieval_data(retrieval_dict)
    return {
        'code': 0,
        'msg': '',
        'data': data
    }


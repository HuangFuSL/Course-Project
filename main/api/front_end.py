from ..db import DataBase
from .model import *

async def heat_map():
    data = await DataBase().get_heatmap_data()
    """返回的样例数据
    [{"count": 6, "lng": 116.612326, "lat": 39.92220205},
    {"count": 22, "lng": 116.3307066, "lat": 40.07476902}]
    """
    return {
        'code': 0,
        'msg': '',
        'data': data
    }


async def retrieval(item: Retrieval):
    data = await DataBase().get_retrieval_data()
    """
    传入参数见model.py
    返回的样例数据
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

async def graph_1(item: Regression_model):
    data = await DataBase().get_regression_data()
    """
    返回的样例数据
    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']           日期
    [150, 230, 224, 218, 135, 147, 260]                         日期对应的均价 
    """
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


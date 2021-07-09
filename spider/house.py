import asyncio
import json
import math
from typing import Any, Dict

import aiohttp
import parsel

from postprocess import *
from utils import *


class QueueEnd():
    pass


def ratio_processor(s: str) -> float:
    try:
        a, b = s.split('梯')
        b, nul = b.split('户')
        return convert_num(a) / convert_num(b)
    except ValueError:
        return 0


def direction_processor(s: str) -> int:
    directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北']
    ret = 0
    for _ in s.split():
        if _ in directions:
            ret += 2 ** directions.index(_)
    return ret


_CLEANER = Processor()
_CLEANER.addSplitter('floor', ' ', False, 'floor_no', 'num_floor')

_CLEANER.addDate('listing_time', '%Y年%m月%d日')
_CLEANER.addDate('last_trade_time', '%Y年%m月%d日')

_CLEANER.addCustom('elevator_ratio', ratio_processor)
_CLEANER.addCustom('direction', direction_processor)

_CLEANER.addExtractor('construct_time', False)
_CLEANER.addExtractor('house_type', False, 'bedroom',
                      'living_room', 'bathroom')
_CLEANER.addExtractor('num_floor', False)
_CLEANER.addExtractor('construct_time', False)
_CLEANER.addExtractor('outer_square', False)
_CLEANER.addExtractor('inner_square', False)

_CLEANER.addEncoder('structure', {
    '平层': 0,
    '复式': 1,
    '错层': 2,
    '暂无数据': 3
}, -1)
_CLEANER.addEncoder('construction_type', {
    '塔楼': 0,
    '板楼': 1,
    '板塔结合': 2,
    '平房': 3,
}, -1)
_CLEANER.addEncoder('floor_no', {
    '高楼层': 0,
    '中楼层': 1,
    '低楼层': 2,
    '底层': 3,
    '顶层': 4,
    '地下室': 5,
}, -1)
_CLEANER.addEncoder('construction_struct', {
    '钢混结构': 0,
    '混合结构': 1,
    '砖混结构': 2,
    '砖木结构': 3,
    '钢结构': 4,
    '未知结构': 5,
}, -1)
_CLEANER.addEncoder('trade_property_right', {
    '商品房': 0,
    '私产': 1,
    '已购公房': 2,
    '央产房': 3,
    '二类经济适用房': 4,
    '限价商品房': 5,
    '定向安置房': 6,
}, -1)
_CLEANER.addEncoder('house_life', {
    '满五年': 0,
    '满两年': 1,
    '未满两年': 2,
    '暂无数据': 3,
}, -1)
_CLEANER.addEncoder('house_usage', {'普通住宅': 0, '公寓/住宅': 1, '公寓': 2}, -1)
_CLEANER.addEncoder('property_right', {'共有': 0, '非共有': 1}, -1)
_CLEANER.addEncoder('decoration', {'精装': 0, '简装': 1, '其他': 2, '毛坯': 3}, -1)
_CLEANER.addEncoder('heating', {'集中供暖': 0, '自供暖': 1}, -1)
_CLEANER.addEncoder('whether_elevator', {'有': 1}, 0)
_CLEANER.addEncoder('mortgage_info', {'无抵押': 0, '有抵押': 1}, -1)

_CLEANER.addConverter('outer_square', float)
_CLEANER.addConverter('inner_square', float)
_CLEANER.addConverter('price_per_square', int)
_CLEANER.addConverter('beike_ID', int)
_CLEANER.addConverter('construct_time', int)
_CLEANER.addConverter('num_floor', int)
_CLEANER.addConverter('bedroom', int)
_CLEANER.addConverter('living_room', int)
_CLEANER.addConverter('bathroom', int)

async def upload(body: Dict[str, Any]):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post('http://localhost:8000/upload', data=json.dumps(body), headers={'Content-Type': 'application/json'}) as s:
                print(await s.json())
    except:
        return


async def post_process(queue_in: asyncio.Queue):
    '''
    {'link': 'https://bj.ke.com/ershoufang/101112085073.html', 'city': '北京', 'title': '苹果南区 观花园大两居 满五年唯一 客厅面宽4.4米', 'price': '819', 'price_per_square': '86989', 'construct_time': '2005年建/板楼', 'community_name': '苹果社区南区', 'area': '朝阳', 'street': '双井', 'beike_ID': '101112085073', 'house_type': '2室1厅1卫', 'floor': '低楼层 (共22层)', 'outer_square': '94.15㎡', 'structure': '平层', 'inner_square': '76.65㎡', 'construction_type': '板楼', 'direction': '东北', 'construction_struct': '钢混结构', 'decoration': '精装', 'elevator_ratio': '两梯八户', 'heating': '集中供暖', 'whether_elevator': '有', 'listing_time': '2021年06月28日', 'trade_property_right': '私产', 'last_trade_time': '2006年07月12日', 'house_usage': '普通住宅', 'house_life': '满五年', 'property_right': '非共有', 'mortgage_info': '无抵押', 'num_room': '', 'bedroom': '', 'living_room': '', 'bathroom': '', 'num_floor': ''}
    '''

    fields = None
    records = []

    while True:
        record = await queue_in.get()
        if isinstance(record, QueueEnd):
            await queue_in.put(QueueEnd())
            break

        record = _CLEANER(**record)

        if len(records) < 20:
            records.append(record)
            continue

        body = {
            'content': records,
            'count': len(records)
        }

        await upload(body)

        records.clear()

    if records:
        body = {
            'content': records,
            'count': len(records)
        }

        await upload(body)


async def get_page(url: str) -> parsel.Selector:
    async with aiohttp.ClientSession() as s:
        while True:
            try:
                async with s.get(url, headers=headers) as resp:
                    return parsel.Selector(await resp.text())
            except:
                await asyncio.sleep(10)
                continue

actions = {
    'get_block_names':  "//*[@id=\"beike\"]/div[1]/div[3]/div[1]/dl[2]/dd[1]/div[1]/div[1]/a/@href",
    'get_house_num':    "//*[@id=\"beike\"]/div[1]/div[4]/div[1]/div[2]/div[1]/h2[1]/span[1]/text()",
    'get_2nd_block':    "//*[@id=\"beike\"]/div[1]/div[3]/div[1]/dl[2]/dd[1]/div[1]/div[2]/a/@href"
}


async def get_block_names(city: str):
    url = "https://{city}.ke.com/ershoufang/".format(city=city)
    return (await get_page(url)).xpath(actions['get_block_names']).getall()


async def get_house_num(city: str, blk: str) -> int:
    url = "https://{city}.ke.com{blk}".format(city=city, blk=blk)
    return int((await get_page(url)).xpath(actions['get_house_num']).get())


async def get_2nd_block(city: str, blk: str):
    url = "https://{city}.ke.com{blk}".format(city=city, blk=blk)
    return (await get_page(url)).xpath(actions['get_2nd_block']).getall()


dic = {
    '房屋户型': 'house_type',
    '所在楼层': 'floor',
    '建筑面积': 'outer_square',
    '户型结构': 'structure',
    '套内面积': 'inner_square',
    '建筑类型': 'construction_type',
    '房屋朝向': 'direction',
    '建筑结构': 'construction_struct',
    '装修情况': 'decoration',
    '梯户比例': 'elevator_ratio',
    '供暖方式': 'heating',
    '配备电梯': 'whether_elevator',
    '挂牌时间': 'listing_time',
    '交易权属': 'trade_property_right',
    '上次交易': 'last_trade_time',
    '房屋用途': 'house_usage',
    '房屋年限': 'house_life',
    '产权所属': 'property_right',
    '抵押信息': 'mortgage_info',
    '室': 'bedroom',
    '厅': 'living_room',
    '卫': 'bathroom',
    '总楼层数': 'num_floor'}
dic_city = {
    'bj': '北京',
    'tj': '天津',
    'sh': '上海',
    'sz': '深圳',
    'xm': '厦门',
    'cd': '成都',
    'sjz': '石家庄',
    'zz': '郑州',
    'cq': '重庆'
}

headers = {
    'Cookie': 'lianjia_uuid=53bc921d-ebc2-4057-a76d-27a1f40db3bc; select_city=110000; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217a317dcd708b0-01f42110e978c1-6373267-1500000-17a317dcd71bc8%22%2C%22%24device_id%22%3A%2217a317dcd708b0-01f42110e978c1-6373267-1500000-17a317dcd71bc8%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; lianjia_ssid=8e40e74f-066b-492e-9a35-5cf02c04a77c; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1624327969,1625303623,1625307418; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1625307465; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiNzAzYjM5ZGZjOGNhNTMxZDhkZTEyNDA3NjgxNDhlYzEzMDA0YjZiMTM1Y2Y1YjY3MWUzZmU0OWNkODFhZTU5MTdkMGM2YTgxMmE1NDQ4YWE5NTE0NGI2MjYzN2ViYmU0N2E3ZWIzOTE0OTA2ZmFhZDgwYzY4YWY2OTAwM2U3MTUzMWNjNjIzMmUzZDQ5MzdjOGRiNGVmY2QwNDA1OTIwOWQ3MWVmNjA2NjVjNWMwN2FhNGI1NDc1ZDI4OTAxNmE4NTExZmM0ZGUxYzZiMzg4MmE5ZGMyZTgxNDMxZTZhNTE0YmQzMDdhNDA5YmMyNDJjNjVjZDdmZjI5ZTA3MmJjMWM1MDY4Zjg0ODU0ZWJjYzg5Y2RiM2M4ZDIzZGZkNzUxNTJiNDAyN2FmMzhhMDc5YThjMjJiZGM1ZTQ0NjdiYjU3ZTczZjAwMTBlMTQ1YmM4YzU2MWU0ZGQ0YjQ5NGM2NFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCJiNDlmYjdlZVwifSIsInIiOiJodHRwczovL2JqLmtlLmNvbS9lcnNob3VmYW5nL2Zlbmd0YWkvIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}


async def process_page(url: str, city_code: str) -> Dict[str, Any]:
    '''
    获取并处理一个页面的信息

    参数：URL、城市代码
    返回值：房源信息（以字典形式表示）

    示例URL：

    https://bj.ke.com/ershoufang/101112085073.html?fb_expo_id=463467750376390656
    '''
    selector = await get_page(url)

    house_info = {'link': url}
    house_info['city'] = dic_city[city_code]

    # 首页信息提取
    root = '//*[@id="beike"]/div[1]/div[4]/div[1]/div[2]'
    attrs = {
        'title':            '//h1/text()',                                 # 房源标题
        # 房源总价
        'price':            root + '/div[2]/span[1]/text()',
        # 房源单价
        'price_per_square': root + '/div[2]/div[1]/div[1]/span/text()',
        # 建设时间
        'construct_time':   root + '/div[3]/div[3]/div[2]/text()',
        'community_name':   root + '/div[4]/div[1]/a[1]/text()',           # 小区
        'area':             root + '/div[4]/div[2]/span[2]/a[1]/text()',   # 区
        'street':           root + '/div[4]/div[2]/span[2]/a[2]/text()',   # 街道
        # 贝壳ID
        'beike_ID':         root + '/div[4]/div[4]/span[2]/text()'
    }
    for k, v in attrs.items():
        house_info[k] = selector.xpath(v).extract_first('').strip()

    # 详情页信息提取
    # 一共有两块，即“基本属性”与“交易属性”两个div内的数据
    # 先用xpath分块，再用正则表达式处理
    def extract_xpath(content: parsel.Selector, xpath: str, name_mapping: Dict[str, str]) -> Dict[str, Any]:
        ret = {}
        for _ in content.xpath(xpath):
            key, value, *nul = filter(None, (i.strip() for i in _.re('>([\s\S]*?)<')))
            if key in name_mapping:
                ret[name_mapping[key]] = value.strip()

        return ret


    for _ in range(2):
        # 基本属性与交易属性是两个相邻的div
        xpath = '//*[@id="introduction"]/div/div/div[{0}]/div[2]/ul/li'.format(
            _ + 1)
        house_info.update(extract_xpath(selector, xpath, dic))

    for _ in dic.values():
        if _ not in house_info:
            house_info[_] = ''

    return house_info


async def worker_wrapper(queue_in: asyncio.Queue, queue_out: asyncio.Queue) -> None:
    while True:
        url, city_code = await queue_in.get()
        await queue_out.put(await process_page(url, city_code))
        print(url, queue_out.qsize())


async def get_page_houses(queue_in: asyncio.Queue, queue_out: asyncio.Queue) -> None:
    while True:
        url, city_code = await queue_in.get()
        selector = await get_page(url)
        for _ in selector.xpath('//li/div/div[1]/a/@href').getall():
            if _[-4:] == 'html':
                await queue_out.put((_, city_code))


async def get_city_metas(queue_in: asyncio.Queue, queue_out: asyncio.Queue):

    while True:
        city_code = await queue_in.get()
        blk_names = await get_block_names(city_code)
        for blk in blk_names:
            num = await get_house_num(city_code, blk)
            if num <= 3000:
                for _ in range(1, math.ceil(num / 30) + 1):
                    await queue_out.put((
                        "https://{0}.ke.com{1}pg{2}".format(city_code, blk, _),
                        city_code
                    ))
            else:
                blk2_names = await get_2nd_block(city_code, blk)
                for blk2 in blk2_names:
                    num = await get_house_num(city_code, blk2)
                    for _ in range(1, math.ceil(min(num / 30, 100)) + 1):
                        await queue_out.put((
                            "https://{0}.ke.com{1}pg{2}".format(
                                city_code, blk2, _),
                            city_code
                        ))



async def main():
    o, a, b, c = [asyncio.Queue() for _ in range(4)]

    while True:
        cities = ['sh', 'bj',  'gz', 'sz']
        for _ in cities:
            await o.put(_)

        stage1 = [get_city_metas(o, a)]
        stage2 = [get_page_houses(a, b) for _ in range(10)]
        stage3 = [worker_wrapper(b, c) for _ in range(40)]
        stage4 = [post_process(c) for _ in range(20)]

        works = stage1 + stage2 + stage3 + stage4
        await asyncio.wait(works, return_when=asyncio.ALL_COMPLETED)

        await asyncio.sleep(86400)


if __name__ == "__main__":
    print(asyncio.run(main()))

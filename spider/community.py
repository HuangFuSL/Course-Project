from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, overload

import aiohttp
import parsel
from xpinyin import Pinyin

from const import *
from postprocess import *
from utils import *

_SERVER = 'http://127.0.0.1:8000/'

_URL = 'https://{city}.ke.com/xiaoqu/rs{name}/'
_XPATH = '//*[@id="beike"]/div[1]/div[4]/div[1]/div[3]/ul/li/div[1]/div/a/text()'
_XSALE = '//*[@id="beike"]/div[1]/div[4]/div[1]/div[3]/ul/li/div[2]/div[2]/a/span/text()'
_ATTRS = ['community_name', 'district', 'street']

_CLEANER = Processor()
_CLEANER.addExtractor('num_on_sale', False)
_CLEANER.addConverter('num_on_sale', int)

@overload
async def get_page(url: str, json_: bool = True, params: Dict[str, Any] = {}) -> Any:
    ...


@overload
async def get_page(url: str, json_: bool = False, params: Dict[str, Any] = {}) -> parsel.Selector:
    ...


async def get_page(url: str, json_: bool = False, params: Dict[str, Any] = {},) -> parsel.Selector | Any:
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params) as resp:
            if json_:
                content = json.loads(await resp.text())
            else:
                content = parsel.Selector(await resp.text())
    return content

async def get_community_info(city: str, name: str):
    city_code = Pinyin().get_initials(city, '').lower()
    url = _URL.format(city=city_code, name=name)
    selector = await get_page(url)
    content = selector.xpath(_XPATH).getall()

    if len(content) > 3:
        del content[1]

    ret = {k: v for k, v in zip(_ATTRS, content)}

    ret['num_on_sale'] = selector.xpath(_XSALE).get()
    ret['city'] = city
    return _CLEANER(**ret)


async def query_community_loc(community_name: str, city: str, district: str, street: str, **kwargs):
    params = {
        'address': ' '.join([district, street, community_name]),
        'city': city,
        'ak': AK,
        'output': 'json'
    }
    url = 'http://api.map.baidu.com/geocoding/v3/' + '?' + \
        '&'.join('{k}={v}'.format(k=k, v=v) for k, v in params.items())
    url = get_key(url, SK)
    
    while True:
        resp = await get_page(url, json_=True)

        if resp['status'] == 0:
            return resp['result']['location']
        
        await asyncio.sleep(3600)

async def query_subway_loc(lat: float, lng: float, **kwargs):
    params = {
        'query': '地铁站',
        'location': ','.join(map(str, [lat, lng])),
        'radius': 2500,
        'output': 'json',
        'scope': 2,
        'ak': AK,
        'radius_limit': 'true'
    }
    url = 'https://api.map.baidu.com/place/v2/search' + '?' + \
        '&'.join('{k}={v}'.format(k=k, v=v) for k, v in params.items())

    while True:
        url = get_key(url, SK)
        resp = await get_page(url, json_=True)

        if resp['status'] == 0:
            return {'subway': [
                {'station_name': _['name'], 'distance': _['detail_info']['distance']}
                for _ in resp['results']
            ]}
        await asyncio.sleep(3600)

async def compose(city: str, name: str):
    content = await get_community_info(city, name)
    content.update(await query_community_loc(**content))
    content.update(await query_subway_loc(**content))
    return content

async def get_all_cities() -> List[str]:
    resp = await get_page(_SERVER + 'querycity/', json_=True)
    return resp['data']

async def process_communities(city: str) -> bool:
    url = _SERVER + 'uploadcommunity/'
    resp = await get_page(url, json_=True, params={'city': city})
    if not resp['data']:
        return False

    payload = {'count': 0, 'content': []}
    for _ in resp['data']:
        payload['content'].append(await compose(city, _))
    
    payload['count'] = len(payload['content'])
    print(payload)
    async with aiohttp.ClientSession() as c:
        async with c.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}) as resp:
            print(await resp.json())

    return True

async def main():
    while True:
        for city in await get_all_cities():
            while await process_communities(city):
                pass
        await asyncio.sleep(3600)

if __name__ == '__main__':
    print(asyncio.run(main()))

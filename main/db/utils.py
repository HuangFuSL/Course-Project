import datetime
import functools
import math
import operator
from typing import Any, Dict, List, Tuple

_RADIUS = 6371.393

def clean(*args: str, **kwargs: Any) -> Dict[str, Any]:
    return {_: kwargs[_] for _ in args if _ in kwargs}


def split_records(src: List[Dict[str, Any]], a: List[str], b: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    return [clean(*a, **_) for _ in src], [clean(*b, **_) for _ in src]


def extract_field(src: List[Dict[str, Any]], fieldname: str) -> Tuple[List[Any], List[Dict[str, Any]]]:
    x, y = [], []

    for _ in src.copy():
        x.append(_[fieldname])
        del _[fieldname]
        y.append(_)

    return x, y

def add_field(src: List[Dict[str, Any]], new: Dict[str, Any]) -> List[Dict[str, Any]]:
    for _ in src:
        _.update(new)

    return src

def flatten(src: Any) -> List[Any]:
    if isinstance(src, list):
        if not src:
            return []
        return functools.reduce(operator.add, map(flatten, src))
    else:
        return [src]

def to_deg(_: float) -> float:
    return 180 * _ / math.pi

def calc_lng_range(lng: float, lat: float, dist: int) -> Tuple[float, float]:
    radius = math.cos(lat) * _RADIUS
    half_int = dist / radius
    x, y = lng - half_int, lng + half_int
    if x < -180:
        x += 180
    if y > 180:
        y -= 180
    return x, y

def calc_lat_range(lng: float, lat: float, dist: int) -> Tuple[float, float]:
    return min(-90, lat - dist / _RADIUS), max(90, lat - dist / _RADIUS)


def get_today() -> datetime.date:
    tz_info = datetime.timezone(datetime.timedelta(hours=8))
    current = datetime.datetime.now()
    return current.astimezone(tz_info).date()

def get_years_ago(years: int) -> datetime.date:
    return get_today() - datetime.timedelta(days=int(years * 365.25))
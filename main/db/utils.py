from typing import Any, Dict, List, Tuple
import operator
import functools


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
from typing import Any, Dict, List, Tuple


def clean(*args: str, **kwargs: Any) -> Dict[str, Any]:
    return {_: kwargs[_] for _ in args if _ in kwargs}


def split_records(src: List[Dict[str, Any]], a: List[str], b: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    return [clean(*a, **_) for _ in src], [clean(*b, **_) for _ in src]


def extract_field(src: List[Dict[str, Any]], fieldname: str) -> Tuple[List[Dict[str, Any]], List[Any]]:
    x, y = [], []

    for _ in src.copy():
        x.append(_[fieldname])
        del _[fieldname]
        y.append(_)

    return x, y

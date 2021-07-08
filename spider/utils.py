import hashlib
import urllib.parse as parse

def clean(*args, **kwargs):
    return {_: kwargs[_] for _ in args if _ in kwargs}


def convert_num(obj: str):
    mapping = {
        '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
    }
    split = obj.split('十')
    if len(split) != 1:
        a, b = split
        x, y = mapping.get(a, 1), mapping.get(b, 0)
        return 10 * x + y
    else:
        return mapping[obj]

def get_key(url: str, sk: str):
    parsed = parse.urlparse(url)
    url_ = '{2}?{4}'.format(*parsed)
    raw = parse.quote_plus(parse.quote(url_, safe="/:=&?#+!$,;'@()*[]") + sk)
    sn = hashlib.md5(raw.encode()).hexdigest()
    return parse.quote(url, safe="/:=&?#+!$,;'@()*[]") + '&sn=' + sn

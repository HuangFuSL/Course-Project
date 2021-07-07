from typing import Any, Dict


def wrap_response(content: Any) -> Dict[str, Any]:
    return {
        'code': 0,
        'msg': '',
        'data': content
    }

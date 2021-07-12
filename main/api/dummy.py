from ..db import DataBase
from .utils import *


async def execute_SQL(command: str):
    return wrap_response(await DataBase().execute(command))

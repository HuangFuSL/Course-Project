from ..db import DataBase
async def startup_event():
    await DataBase().create_table()

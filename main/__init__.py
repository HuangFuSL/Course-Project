from typing import Optional, List
from .model import *
from .db import DataBase
from fastapi import FastAPI

app = FastAPI()

instance = DataBase()



@app.post("/upload/")
async def create_house_info_daily(item: HousePostFormat):
    print(len(item.content))
    return {'code': 0}

@app.get("/heatmap/")
async def Heat_map(item: Heat_map):
     return item

@app.get("/retrieval/")
async def Retrieval(item: Retrieval):
     return item

@app.get("/regression/")
async def Regression_model(item: Regression_model):
     return item


@app.get("/")
async def home():
     await instance.create_table()
     return {"code": 0}

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from .api import *
from .db import DataBase
from .model import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instance = DataBase()


app.on_event("startup")(startup_event)
app.post("/upload/")(add_house)
app.get('/dummyheatmap/')(dummy_heat_map)

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

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from .api import *
from .db import DataBase

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
app.get('/uploadcommunity/')(query_community)
app.get('/querycity/')(query_cities)
app.post('/uploadcommunity/')(add_community)
app.get('/heatmap/')(heat_map)
app.get('/retrieval/')(retrieval)
app.get("/regression/")(regression_model)
app.get('/sql/')(execute_SQL)


@app.get("/")
async def home():
     await instance.create_table()
     return {"code": 0}

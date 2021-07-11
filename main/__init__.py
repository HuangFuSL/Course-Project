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
app.get('/heatmap_1/')(heat_map_1)
app.get('/heatmap_2/')(heat_map_2)
app.post('/retrieval/')(retrieval)
app.post('/graph_1/')(graph_1)
app.post('/graph_2/')(graph_2)
app.post('/graph_3/')(graph_3)
app.post('/graph_4/')(graph_4)
app.post('/graph_5/')(graph_5)
app.post('/graph_6/')(graph_6)
app.post('/graph_7/')(graph_7)
app.post('/graph_8/')(graph_8)
app.post('/graph_9/')(graph_9)
app.post('/graph_10/')(graph_10)
app.post('/graph_11/')(graph_11)
app.post('/graph_12/')(graph_12)
app.get("/regression/")(regression_model)
app.get('/sql/')(execute_SQL)


@app.get("/")
async def home():
     await instance.create_table()
     return {"code": 0}

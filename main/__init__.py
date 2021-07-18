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
app.post("/api/upload/")(add_house)
app.get('/api/uploadcommunity/')(query_community)
app.get('/api/querycity/')(query_cities)
app.post('/api/uploadcommunity/')(add_community)
app.get('/api/heatmap_1/')(heat_map_1)
app.get('/api/heatmap_2/')(heat_map_2)
app.post('/api/retrieval/')(retrieval)
app.post('/api/graph_1/')(graph_1)
app.post('/api/graph_2/')(graph_2)
app.post('/api/graph_3/')(graph_3)
app.post('/api/graph_4/')(graph_4)
app.post('/api/graph_5/')(graph_5)
app.post('/api/graph_6/')(graph_6)
app.post('/api/graph_7/')(graph_7)
app.post('/api/graph_8/')(graph_8)
app.post('/api/graph_9/')(graph_9)
app.post('/api/graph_10/')(graph_10)
app.post('/api/graph_11/')(graph_11)
app.post('/api/graph_12/')(graph_12)
app.post("/api/regression/")(regression_model)
app.get('/api/sql/')(execute_SQL)

from fastapi import FastAPI, Request, Body, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import logging
import numpy as np

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
path = "train_new.csv"

df = pd.read_csv(path)

async def sentiment_analysis():
    sentiment = df[df['sentiment'] != 'ignored'].groupby('sentiment').size()
    data_sentiment = sentiment.tolist()
    return_data = {"data": data_sentiment}
    return return_data

async def aspect_analysis():
    labels = ['ac_P1','air_panas_P1','bau_P1','general','kebersihan','linen_P1','service','sunrise_meal_P1','tv_P1','wifi_P1']
    neg = []
    pos = list()
    for label in labels:
        sentiment_aspect = df[df['category'] == label].groupby(['sentiment']).size()
        sentiment_aspect = sentiment_aspect.tolist()
        neg.append(sentiment_aspect[0])
        pos.append(sentiment_aspect[1])

    data = {"labels": labels, "negatif": neg,"positif":pos}
    return data

@app.get("/")
async def home(request: Request):
    sentiment = await sentiment_analysis()
    aspect = await aspect_analysis()
    print(aspect)
    return templates.TemplateResponse("index.html", context={"request": request,"data_sentiment":sentiment})

@app.get("/coba")
async def coba(request: Request):
    sentiment = await sentiment_analysis()
    return sentiment

@app.get("/sentiment_aspect")
async def sentiment_aspect(request: Request):
    aspect = await aspect_analysis()
    return aspect

@app.get("/room_aspect")
async def room_aspect(request: Request):
    labels = ['Single', 
        'Twin',
        'Double', 
        'Superior',
        'Deluxe', 
        'Suite', ]
    neg = []
    pos = list()
    for label in labels:
        sentiment_aspect = df[df['room'] == label].groupby(['sentiment']).size()
        sentiment_aspect = sentiment_aspect.tolist()
        neg.append(sentiment_aspect[1])
        pos.append(sentiment_aspect[2])

    data = {"labels": labels, "negatif": neg,"positif":pos}
    return data

@app.get("/sentiment")
async def sentiment(request: Request):
    return templates.TemplateResponse("sentiment.html", context={"request": request})






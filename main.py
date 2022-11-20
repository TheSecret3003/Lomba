from fastapi import FastAPI, Request, Body, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import logging
import numpy as np
import re
import string
from scipy.special import softmax
from simpletransformers.classification import ClassificationModel
import os
from starlette.responses import HTMLResponse 
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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

aspect_categories = ['wifi_P1',
 'kebersihan',
 'bau_P1',
 'service',
 'linen_P1',
 'ac_P1',
 'sunrise_meal_P1',
 'general',
 'air_panas_P1',
 'tv_P1']

def generate_sentence_pair(ulasan):
    sentence_pairs = []
    sentence_pair1 = []
    sentence_pair2 = []
    sentence_pair3 = []
    aspect_sentiment = []
    for i in aspect_categories:
        pair1 = i+"-pos"
        pair2 = i+"-neg"
        sentence_pair1.append(ulasan)
        sentence_pair1.append(pair1)
        sentence_pair2.append(ulasan)
        sentence_pair2.append(pair2)
        sentence_pairs.append(sentence_pair1)
        sentence_pairs.append(sentence_pair2)
        aspect_sentiment.append(pair1)
        aspect_sentiment.append(pair2)
        sentence_pair1 = []
        sentence_pair2 = []
    return sentence_pairs, aspect_sentiment

def clean_text(text):
    text = text.lower()
    text = re.sub('[%s]' % re.escape(string.punctuation.replace('?', '')), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\r', '', text)
    text = text.replace('?', ' ?')
    text = text.replace('\d+', '')
    text = re.sub('[.;:!\'?,\"()\[\]*~]', '', text)
    text = re.sub('(<br\s*/><br\s*/>)|(\-)|(\/)', '', text)
    text = re.sub(r"^(â€œ)", "" ,text)
    return text

model = ClassificationModel('bert', "model", use_cuda=False, 
        args={"use_multiprocessing": False, 
              "use_multiprocessing_for_evaluation": False, 
              "process_count": 1,
              "silent" : False}) 

@app.get("/prediction")
async def make_prediction(ulasan):
    sentence_pairs, aspect_sentiment = generate_sentence_pair(ulasan)
    predictions, raw_outputs = model.predict(sentence_pairs)
    test = pd.DataFrame(columns=["aspect-sentiment","label"])
    test['aspect-sentiment'] = aspect_sentiment
    test['label'] = predictions
    result = test[test['label'] == 1]
    pattern = 'pos|neg'
    results = result['aspect-sentiment'].str.contains(pattern)
    sentiments = []
    for sentiment in result[results]['aspect-sentiment'].tolist():
        sentiments.append(sentiment)
    return sentiments


@app.post("/sentiment")
async def handle_form(request: Request,sentence: str = Form(...)):
    sentence_pairs, aspect_sentiment = generate_sentence_pair(sentence)
    predictions, raw_outputs = model.predict(sentence_pairs)
    sentiments = []
    for i in range(len(predictions)):
        if predictions[i] == 1:
            sentiments.append(aspect_sentiment[i])
    data = {'aspect':aspect_sentiment,'sentiment':predictions}
    
    # sentiments = await make_prediction(sentence)
    return templates.TemplateResponse("sentiment_result.html", context={"request": request,"data":sentiments})





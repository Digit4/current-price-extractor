from bs4 import BeautifulSoup as soup
from flask import Flask
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/<exchange>/<ticker>')
def getTickerData(exchange,ticker):

    base_url = "https://www.google.com/finance/search?tbm=fin&q="
    try:
        response = requests.get(f"{base_url}{exchange}:{ticker}")
    except Exception as exc:
        return exc

    try:
        page_soup = soup(response.text,'html.parser')
    except Exception as exc:
        return exc

    try:
        price_container = page_soup.findAll("div",{"class":"BNeawe iBp4i AP7Wnd"})
    except Exception as exc:
        return exc
    try:
        if(len(price_container)!=0):
            return(price_container[0].text.split(" ")[0].replace(",","")+" "+str(response.status_code))
        else:
            return "-1"
    except Exception as exc:
        return exc
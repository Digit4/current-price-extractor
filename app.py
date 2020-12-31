from bs4 import BeautifulSoup as soup
from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/<exchange>/<ticker>')
def getTickerData(exchange,ticker):
    # exchange="BSE"
    # ticker="INFY"
    base_url = "https://www.google.com/finance/search?tbm=fin&q="
    response = requests.get(f"{base_url}{exchange}:{ticker}")

    page_soup = soup(response.text,'html.parser')

    price_container = page_soup.findAll("div",{"class":"BNeawe iBp4i AP7Wnd"})
    if(len(price_container)!=0):
        return(price_container[0].text.split(" ")[0].replace(",",""))
    else:
        return "-1"
from time import sleep
import requests, json, sys


class Signals:
    def __init__(self):
        self.data_list = []

    def fetch_signals(self, request_url):
        response = requests.get(request_url)
        if response.ok:
            self.data_list = json.loads(response.text)["data"]["signals"]

    def display_signal(self, id):
        if len(self.data_list) != 0:
            print(self.data_list[id]["_id"])
        else:
            print("Fetch Data first")


def fetch_prices(request_url, company_name):
    prices = dict()
    response = requests.get(request_url)
    if response.ok:
        if "-1" not in response.text:
            prices[company_name] = response.text
        else:
            prices[company_name] = -1
    elif response.status_code == 429:
        sleep(30)
        print("429 Occurred, waiting before querying again")
        fetch_prices(request_url, company_name)
    return prices[company_name]


def store_prices(signal_dict, price):
    url = (
        'https://mycycles.in/server/graphql?query=mutation {%0A%20 updatePrice(id%3A "'
        + str(signal_dict["_id"])
        + '"%2C price%3A '
        + str(price)
        + ") {%0A%20%20%20 _id%0A%20%20%20 company_name%0A%20%20%20 price%0A%20 }%0A}%0A"
    )
    response = requests.post(url)
    if response.ok:
        updated_signal_dict = json.loads(response.text)["data"]["updatePrice"]
        print(
            f"Price updated to: {updated_signal_dict['price']} for: {updated_signal_dict['company_name']}"
        )
    else:
        print(response)


if __name__ == "__main__":
    signals = Signals()
    exchange = 'BSE'
    signals.fetch_signals(
        "https://mycycles.in/server/graphql?query=%7B%0A%09signals%7B%0A%20%20%20%20_id%0A%20%20%20%20company_name%0A%20%20%20%20%0A%20%20%7D%0A%7D"
    )
    
    for signal in signals.data_list:
        price = fetch_prices(
            f"https://mycycles.in/flask/{exchange}/{signal['company_name']}",
            signal["company_name"],
        )
        store_prices(signal, price)
        sleep(1)

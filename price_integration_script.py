from time import sleep
from datetime import datetime
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
        try:
            print(
                f"[{datetime.now().isoformat(' ','seconds')}]Price updated to: {updated_signal_dict['price']} for: {updated_signal_dict['company_name']}"
            )
        except Exception as e:
            print(f"Error occurred while printing:{e}")
    else:
        response.raise_for_status()


if __name__ == "__main__":
    signals = Signals()
    exchange = 'BSE'
    start_time = datetime.now()
    print(f"[{start_time.isoformat(' ','seconds')}]Fetching all signals from DB")
    signals.fetch_signals(
        "https://mycycles.in/server/graphql?query=%7B%0A%09signals%7B%0A%20%20%20%20_id%0A%20%20%20%20company_name%0A%20%20%20%20%0A%20%20%7D%0A%7D"
    )
    print(f"[{datetime.now().isoformat(' ','seconds')}]DB signals fetched")
    
    for signal in signals.data_list:
        try:
            price = fetch_prices(
                f"https://mycycles.in/flask/{exchange}/{signal['company_name']}",
                signal["company_name"],
            )
            try:
                store_prices(signal, price)
            except Exception as e:
                print(f"[{datetime.now(' ','seconds')}]Error occurred while storing price for {signal}: {e}")
        except Exception as e:
            print(f"[{datetime.now(' ','seconds')}]Error occurred in fetching price for {signal}: {e}")
        sleep(3)
    end_time = datetime.now()
    print(f"Finished script running successfully. Took {end_time-start_time}")

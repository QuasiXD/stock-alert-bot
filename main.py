import html
import os

import requests
import requests_cache
from dotenv import load_dotenv

load_dotenv()
PRICE_CHANGE_THRESHOLD = 4.00
CACHE_EXPIRY_MINS = 10
NEWS_COUNT = 3
requests_cache.install_cache("app_cache",expire_after=CACHE_EXPIRY_MINS*60)

STOCK = "TSLA"
COMPANY_NAME = "Tesla"


ALPHA_ENDPOINT = "https://www.alphavantage.co/query"
ALPHA_API_KEY = os.environ["ALPHA_API_KEY"]

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ["NEWS_API_KEY"]

TELEGRAM_BOT_TOKEN = os.environ["BOT_ID"]
TELEGRAM_CHAT_TOKEN = os.environ["CHAT_ID"]
TELEGRAM_ENDPOINT = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
def get_stock_prices():
    parameters = {
        "function":"TIME_SERIES_DAILY",
        "apikey":ALPHA_API_KEY,
        "symbol":STOCK,
    }

    response = requests.get(url=ALPHA_ENDPOINT,params=parameters)
    response.raise_for_status()
    data = response.json()

    daily = data["Time Series (Daily)"]
    closes = [float(v["4. close"]) for v in list(daily.values())[:2]]
    latest_close, previous_close = closes

    price_change = latest_close-previous_close
    is_increase = price_change > 0
    percent_change = round(abs(price_change)/previous_close * 100,2)
    return percent_change,is_increase

def get_news():
    parameters = {
        "apiKey":NEWS_API_KEY,
        "q":COMPANY_NAME,
        "pageSize":NEWS_COUNT,
        "language":"en",
        "sortBy":"publishedAt",
        "searchIn":"title"
    }
    response = requests.get(url=NEWS_ENDPOINT,params=parameters)
    response.raise_for_status()
    data = response.json()
    articles = data["articles"]
    titles = [article["title"] or "" for article in articles]
    descriptions = [article["description"] or "" for article in articles]
    return titles,descriptions



def send_telegram_messages(titles,descriptions,is_increase,percent_change):
    indicator = "🔺" if is_increase else "🔻"
    for index in range(NEWS_COUNT):
        title = titles[index]
        description = descriptions[index]
        response = requests.post(url=TELEGRAM_ENDPOINT,data={
            "chat_id": TELEGRAM_CHAT_TOKEN,
            "text":f"{STOCK}: {indicator}{percent_change}%\n<b>{html.escape(title)}</b>\n\n{html.escape(description)}",
            "parse_mode":"HTML"
        }
        )
        response.raise_for_status()
        print("Message Successfully Sent!")

if __name__ == "__main__":
    percent_change,is_increase = get_stock_prices()
    if percent_change >= PRICE_CHANGE_THRESHOLD:
        titles,descriptions = get_news()
        send_telegram_messages(titles,descriptions,is_increase,percent_change)

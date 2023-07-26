import time
from yahooquery import Ticker
import smtplib
import ssl
import certifi
import requests
import re

ssl_context = ssl.create_default_context(cafile=certifi.where())
market_price = 100
is_warning = False
is_green = False
SERVER = 'smtp.gmail.com'
PORT = 465
FROM = 'insightfulportfolios@gmail.com'
PASSWORD = "dooxbfadafcucdjf"
TO = 'eeswar.kv@gmail.com'

# Email templates
WARNING_SUBJECT = "Warning: Time To Buy GNA"
WARNING_BODY = "Hi, the GNA stock price is lower than 911 now!"

GREEN_SUBJECT = "Good News: GNA Price Increase"
GREEN_BODY = "Hi, the GNA stock price is now higher than 912!"

url = "https://api.ultramsg.com/instance55310/messages/chat"


def retrieve_stock_symbol():
    ticker = Ticker('GNA.NS')
    history = ticker.history(period="1d")
    current_price = history["close"].iloc[-1]
    return current_price

def registration_message(number, email):
    REG_SUBJECT = "Insightful Portfolios"
    REG_BODY = "Thanks for registering with Insightful Portfolios!"

    number_without_plus = re.sub(r'\+', '', number)
    print(number_without_plus)
    payload = f"token=e4hz6eak6zxrhv0q&to=%2B{number_without_plus}&body={REG_BODY}"
    payload = payload.encode('utf8').decode('iso-8859-1')
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response)
    with smtplib.SMTP_SSL(SERVER, PORT, context=ssl_context) as server:
        server.login(FROM, PASSWORD)
        server.sendmail(FROM, email, f"Subject: {REG_SUBJECT}\n\n{REG_BODY}")

def main():
    is_green = False
    is_warning = False
    while True:
        stock_symbols = retrieve_stock_symbol()

        if stock_symbols <= 912:
            print("Warning!, stock is now at ", stock_symbols)
            if not is_warning:
                with smtplib.SMTP_SSL(SERVER, PORT, context=ssl_context) as server:
                    server.login(FROM, PASSWORD)
                    server.sendmail(FROM, TO, f"Subject: {WARNING_SUBJECT}\n\n{WARNING_BODY}")
            is_warning = True
            is_green = False
        elif stock_symbols >= 913:
            print("Good News!, stock is now at ", stock_symbols)
            if not is_green:
                with smtplib.SMTP_SSL(SERVER, PORT, context=ssl_context) as server:
                    server.login(FROM, PASSWORD)
                    server.sendmail(FROM, TO, f"Subject: {GREEN_SUBJECT}\n\n{GREEN_BODY}")
            is_green = True
            is_warning = False
        else:
            print("Stock is at ", stock_symbols)

        # Wait for 30 seconds before the next iteration
        time.sleep(30)

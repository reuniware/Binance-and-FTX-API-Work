import glob, os
from datetime import datetime
from datetime import timedelta

import ftx
import pandas as pd
import requests
import threading
import time
import ta
import math
import operator


def log_to_results(str_to_log):
    fr = open("results.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_errors(str_to_log):
    fr = open("errors.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_trades(str_to_log):
    fr = open("trades.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_evol(str_to_log):
    fr = open("evol.txt", "a")
    fr.write(str_to_log + "\n")
    fr.close()


def log_to_file(str_file, str_to_log):
    fr = open(str_file, "a")
    fr.write(str_to_log + "\n")
    fr.close()


# import numpy as npfrom binance.client import Client

ftx_client = ftx.FtxClient(
    api_key='',
    api_secret='',
    subaccount_name=''
)

# result = client.get_balances()
# print(result)

if os.path.exists("results.txt"):
    os.remove("results.txt")

if os.path.exists("errors.txt"):
    os.remove("errors.txt")

if os.path.exists("trades.txt"):
    os.remove("trades.txt")

if os.path.exists("evol.txt"):
    os.remove("evol.txt")

for fg in glob.glob("CS_*.txt"):
    os.remove(fg)

for fg in glob.glob("scan_*.txt"):
    os.remove(fg)

list_results = []
results_count = 0

stop_thread = False

dic_evol = {}
dic_timestamp = {}
dic_last_price = {}

num_req = 0


def scan_one(symbol):
    global num_req
    # print("scan one : " + symbol)

    resolution = 60 * 1
    delta_time = resolution * 1  # on travaille sur n bougies max (en comptant la bougie en cours de formation)

    # while not stop_thread:
    #     try:
    data = ftx_client.get_historical_data(
        market_name=symbol,
        resolution=resolution,
        limit=10000,
        start_time=float(round(time.time())) - delta_time,
        end_time=float(round(time.time())))

    num_req = num_req + 1

    dframe = pd.DataFrame(data)

    # dframe.reindex(index=dframe.index[::-1])
    dframe = dframe.iloc[::-1]

    close0 = 0
    open0 = 0
    try:
        close0 = dframe['close'].iloc[0]
        open0 = dframe['open'].iloc[0]

        close_evol = close0 / open0
        dic_evol[symbol] = close_evol

        # print(symbol + " " + str(close_evol))
    except BaseException as e:
        # log_to_errors(str(datetime.now()) + " " + symbol + " Exception (1) : " + format(e) + " : " + str(close0) + " " + str(open0))
        pass

        # except Exception as e:
        #     # log_to_errors(str(datetime.now()) + " " + symbol + " Exception (2) : " + str(e))
        #     continue
        #
        # finally:
        #     time.sleep(0.25)


def main_thread(name):
    global ftx_client, list_results, results_count, num_req, stop_thread

    # while not stop_thread:

    markets = requests.get('https://ftx.com/api/markets').json()
    df = pd.DataFrame(markets['result'])
    df.set_index('name')

    for index, row in df.iterrows():
        symbol = row['name']
        symbol_type = row['type']

        # if not symbol.endswith("-PERP"):
        #     continue

        try:
            y = threading.Thread(target=scan_one, args=(symbol,))
            y.start()
        except requests.exceptions.ConnectionError:
            continue

    print("All threads started.")

    while not stop_thread:
        sorted_d = dict(sorted(dic_evol.items(), key=operator.itemgetter(1), reverse=True))
        # log_to_results(str(datetime.now()) + " (" + str(num_req) + ') EVOL CLOSE/OPEN : ' + str(sorted_d))
        # print(str(datetime.now()) + " (" + str(num_req) + ') EVOL CLOSE/OPEN : ' + str(sorted_d))
        for key, value in sorted_d.items():
            log_to_results(str(datetime.now()) + " " + key + " " + str(value))
            print(str(datetime.now()) + " " + key + " " + str(value))

        print("All results written ok")

        stop_thread = True


x = threading.Thread(target=main_thread, args=(1,))
x.start()

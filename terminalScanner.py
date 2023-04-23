from binance.client import Client
from binance.websockets import BinanceSocketManager
import logging
import datetime as dt
import time
import sys
from tqdm import tqdm
import simpleaudio as sa
from termcolor import cprint


wave_obj = sa.WaveObject.from_wave_file('alertTone.wav')
global lst, status, color_hex, pricelist, inList

pairs = "BTC"  # BTC/ETH/USDT/BNB/PAX

min_vol = 50.0           # 350.0 MINIMUM VOLUME THRESHOLD
vol_diff_treshold = 0.3  # 0.5 VOLUME DIFFERENCE IN PERCENTAGE THRESHOLD

# START TIME (DO NOT CHANGE)
T = dt.datetime.now()


class CoinData:
    def __init__(self, coinarray):
        self.symbol = coinarray['s']					 # symbol
        self.bid = float(coinarray['b'])			     # best bid price
        self.ask = float(coinarray['a'])			     # best ask price
        self.open = float(coinarray['o'])			     # open price
        self.high = float(coinarray['h'])		         # high price
        self.low = float(coinarray['l'])			     # low price
        self.number_of_trades = float(coinarray['n'])	 # total number of trades
        self.price_change = float(coinarray['p'])		 # price change
        self.percent_change = float(coinarray['P'])		 # % price change
        self.volume = float(coinarray['q'])				 # volume
        self.time_stamp = time.time()


def display(sym, xopen, voldiff, percent_change, pricediff, volume, timestamp):
    if percent_change < 0:
        cprint(f"{sym} :     "
               f"{xopen:.7f}   |  "
               f"DIFF: {round(voldiff, 3)}   |  "
               f"% Change {round(percent_change, 2)}   |  "
               f"Price Diff {round(pricediff, 4)}     |  "
               f"VOL: {round(volume, 1)}   |  "
               f"{timestamp}", 'red')
    else:
        cprint(f"{sym} :     "
               f"{open:.6f}   |  "
               f"DIFF: {round(voldiff, 3)}   |  "
               f"% Change {round(percent_change, 2)}   |  "
               f"Price Diff {round(pricediff, 4)}     |  "
               f"VOL: {round(volume, 1)}   |  "
               f"{timestamp}", 'green')


def message_handler(msg):
    global inList
    for coin in msg:
        x = CoinData(coin)
        if x.symbol[-len(pairs):] == pairs:
            if inList == 0:
                pricelist.append(x)
            elif inList == 1:
                ct = time.time()
                for stored_coin in pricelist:
                    if x.symbol == stored_coin.symbol and (ct - stored_coin.time_stamp) > 1:
                        pricediff = ((x.bid - stored_coin.bid) / stored_coin.bid) * 100
                        voldiff = ((x.volume - stored_coin.volume) / stored_coin.volume) * 100
                        if voldiff > vol_diff_treshold and x.volume > min_vol:
                            sym = str(stored_coin.symbol)
                            # date = x.time_stamp
                            timestamp = dt.datetime.now()
                            timestamp = timestamp.strftime('%H:%M:%S')
                            wave_obj.play()
                            # display(sym, x.open, voldiff, x.percent_change, pricediff, x.volume, timestamp)
                            if x.percent_change < 0:
                                cprint(f"{sym} :     "
                                       f"{x.open:.7f}   |  "
                                       f"DIFF: {round(voldiff, 3)}   |  "
                                       f"% Change {round(x.percent_change, 2)}   |  "
                                       f"Price Diff {round(pricediff, 4)}     |  "
                                       f"VOL: {round(x.volume, 1)}   |  "
                                       f"{timestamp}", 'red')
                            else:
                                cprint(f"{sym} :     "
                                       f"{x.open:.7f}   |  "
                                       f"DIFF: {round(voldiff, 3)}   |  "
                                       f"% Change {round(x.percent_change, 2)}   |  "
                                       f"Price Diff {round(pricediff, 4)}     |  "
                                       f"VOL: {round(x.volume, 1)}   |  "
                                       f"{timestamp}", 'green')

                        stored_coin.bid = x.bid
                        stored_coin.ask = x.ask
                        stored_coin.volume = x.volume
                        stored_coin.time_stamp = ct
    inList = 1


def start():
    global inList, pricelist
    pricelist = []
    inList = 0
    print()
    cprint(f'{"  --------- Python Legion Software I".upper()+"nc. ------------":~^20}',
           'blue',
           attrs=['reverse', 'blink'],
           end='')
    time.sleep(1.5)
    print("\n\n  Initialising scanner...")
    try:
        client = Client()
        bar = tqdm(range(3),
                   bar_format="{percentage:5.0f}% |{bar}| {elapsed}/{remaining}"
                   )
        for barfraccion in bar:
            conn = BinanceSocketManager(client)
            time.sleep(0.5)
            conn.start_ticker_socket(message_handler)
            time.sleep(0.5)
            conn.start()

        print("  Scanner on ...\n")
        cprint(f'{" SYMBOL |     PRICE     |    VOL DIFF   |                                          ".upper():~^20}',
               'white',
               attrs=['reverse', 'blink'],
               end='')
        print()
    except Exception as e:
        logging.exception(e)
        print(e)
        print("Error - exiting...")
        sys.exit(0)


if __name__ == '__main__':
    start()

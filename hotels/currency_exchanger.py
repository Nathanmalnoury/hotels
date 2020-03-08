import json
import os
import random

import pandas as pd
import requests
from singleton.singleton import Singleton

from hotels.proxy_pool import ProxyPool

@Singleton
class CurrencyExchanger:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    timeout = 20
    tokens = ["2ab0a578e59c2ad88e54", "d6e953f1f00fc9e91339", "0c27490e0fd1c6dd6b89", "8a003c09e5e38f87e892"]

    def __init__(self):
        dir_path = os.path.dirname(__file__)
        root_path = os.path.dirname(dir_path)
        self.df_symbols_to_name = pd.read_csv(os.path.join(root_path, "data/money_symbols.csv"))
        self.exchange_rates = {}
        self.base_url = "https://free.currconv.com/api/v7/"

    def _query(self, arg):
        proxy_pool = ProxyPool.instance()
        token = random.choice(self.tokens)
        while True:
            proxy = proxy_pool.get_proxy()
            print(f"using proxy {proxy}")

            try:
                resp = requests.get(
                    url=self.base_url + "convert?q={}&compact=ultra&apiKey={}".format(arg, token),
                    proxies={"http": proxy, "https": proxy},
                    headers=self.headers,
                    timeout=self.timeout)
                print("API request is a success.")
                if resp.ok:
                    break
                else:
                    self.tokens.remove(token)
                    token = random.choice(self.tokens)

            except Exception as e:
                print("Connection Error for proxy {}".format(proxy))
                print(e)
                proxy_pool.remove_proxy(proxy)

        dict_ = json.loads(resp.text)
        for k, v in dict_.items():
            self.exchange_rates[k] = v
        print(self.exchange_rates)

    def get_exchange_rate(self, money_from, money_to="EUR"):
        exchange = "{}_{}".format(money_from, money_to)
        rate = self.exchange_rates.get(exchange)
        print(rate)
        if rate is None:
            print("Unknown Exchange rate '{}'. Requesting API".format(exchange))
            self._query(exchange)

        return self.exchange_rates.get(exchange, None)

    def get_name_from_symbol(self, symb):
        search = self.df_symbols_to_name.loc[self.df_symbols_to_name.symbol == symb, "name"]
        try:
            return search.iloc[0]
        except IndexError:
            return None

    def convert_price(self, price, symb, money_to="EUR"):
        money_from = self.get_name_from_symbol(symb)
        exchange_rate = self.get_exchange_rate(money_from=money_from, money_to=money_to)
        if exchange_rate is not None:
            return price * exchange_rate
        else:
            return None

import json
import logging
import math
import os
import random

import pandas as pd
import requests
from singleton.singleton import Singleton

from hotels.utils.conf_reader import ConfReader
from hotels.proxy_pool import ProxyPool

logger = logging.getLogger("Hotels")


@Singleton
class CurrencyExchanger:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    timeout = 20

    def __init__(self):
        dir_path = os.path.dirname(__file__)
        root_path = os.path.dirname(dir_path)
        self.df_symbols_to_name = pd.read_csv(os.path.join(root_path, "data/money_symbols.csv"))

        self.exchange_rates = {}

        conf = ConfReader.get("conf.ini")
        self.tokens = conf["CURRENCY_API"]["tokens"].split(",")
        self.base_url = conf["CURRENCY_API"]["base_url"]

    def _query(self, arg):
        proxy_pool = ProxyPool.instance()
        token = random.choice(self.tokens)
        while True:
            proxy = proxy_pool.get_proxy()
            logger.debug(f"using proxy {proxy}")

            try:
                resp = requests.get(
                    url=self.base_url + f"convert?q={arg}&compact=ultra&apiKey={token}",
                    proxies={"http": proxy, "https": proxy},
                    headers=self.headers,
                    timeout=self.timeout)
                logger.debug("Request to currency exchanger API is a success.")
                if resp.ok:
                    break
                else:
                    self.tokens.remove(token)
                    token = random.choice(self.tokens)

            except Exception as e:
                logger.warning(f"Connection Error for proxy {proxy}")
                logger.warning(e)
                proxy_pool.remove_proxy(proxy)

        dict_ = json.loads(resp.text)
        for k, v in dict_.items():
            self.exchange_rates[k] = v
        logger.debug(f"Saved exchanged rates: {self.exchange_rates}")

    def get_exchange_rate(self, money_from, money_to="EUR"):
        if money_from == money_to:
            return 1.0
        exchange = f"{money_from}_{money_to}"
        rate = self.exchange_rates.get(exchange)
        if rate is None:
            logger.warning(f"Unknown Exchange rate '{exchange}'. Requesting API")
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
            return self.round(price * exchange_rate)
        else:
            return None

    @staticmethod
    def round(n, decimals=0):
        multiplier = 10 ** decimals
        return int(math.floor(n * multiplier + 0.5) / multiplier)

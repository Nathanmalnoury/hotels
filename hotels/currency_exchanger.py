import json
import os

import pandas as pd
import requests


class CurrencyExchanger:
    def __init__(self, token):
        dir_path = os.path.dirname(__file__)
        root_path = os.path.dirname(dir_path)
        self.df_symbols_to_name = pd.read_csv(os.path.join(root_path, "data/money_symbols.csv"))
        self.token = token
        self.exchange_rates = {}
        self.base_url = "https://free.currconv.com/api/v7/"

    def _query(self, arg):
        query = self.base_url + "convert?q={}&compact=ultra&apiKey={}".format(arg, self.token)
        resp = requests.get(query)
        dict_ = json.loads(resp.text)
        for k, v in dict_.items():
            self.exchange_rates[k] = v
        print(self.exchange_rates)

    def get_exchange_rate(self, money_from, money_to="EUR"):
        exchange = "{}_{}".format(money_from, money_to)
        rate = self.exchange_rates.get(exchange)
        if rate is None:
            self._query(exchange)
        return self.exchange_rates.get(exchange)

    def get_name_from_symbol(self, symb):
        search = self.df_symbols_to_name.loc[self.df_symbols_to_name.symbol == symb, "name"]
        try:
            return search.iloc[0]
        except IndexError:
            return None




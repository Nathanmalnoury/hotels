"""Currency Exchanger class."""
import json
import logging
import math
import os

import pandas as pd

from hotels.scrappers.scrapper import Scrapper
from hotels.utils.conf import Conf
from hotels.utils.singleton import singleton

logger = logging.getLogger("Hotels")


@singleton
class CurrencyExchanger:
    """Use an API to convert prices."""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    timeout = 20

    def __init__(self):
        """
        Initialise Currency Exchanger.

        As this is a singleton, this code will only be executed on first call, making every next one useless.
        """
        dir_path = os.path.dirname(__file__)
        root_path = os.path.dirname(dir_path)
        self.df_symbols_to_name = pd.read_csv(os.path.join(root_path, "data/money_symbols.csv"))

        self.exchange_rates = {}

        conf = Conf()
        self.token = conf["CURRENCY_API"]["token"]
        self.base_url = conf["CURRENCY_API"]["base_url"]

    def _query(self, arg, use_proxy):
        url = self.base_url + f"convert?q={arg}&compact=ultra&apiKey={self.token}"
        resp = Scrapper(url).simple_request(use_proxy=use_proxy)

        dict_ = json.loads(resp.text)
        for k, v in dict_.items():
            self.exchange_rates[k] = v
        logger.debug(f"Saved exchanged rates: {self.exchange_rates}")

    def get_exchange_rate(self, money_from, money_to="EUR", use_proxy=True):
        """
        Get an exchange rate, requesting the API if needed.

        :param money_from: code of the currency in which the price to convert is expressed in.
        :type money_from: str
        :param money_to: code of the currency to get the price expressed in.
        :type money_to: str
        :param use_proxy: True to use proxy, False otherwise
        :return: exchange rate
        :rtype: float
        """
        if money_from == money_to:
            return 1.0
        exchange = f"{money_from}_{money_to}"
        rate = self.exchange_rates.get(exchange)
        if rate is None:
            logger.warning(f"Unknown Exchange rate '{exchange}'. Requesting API")
            self._query(exchange, use_proxy=use_proxy)

        return self.exchange_rates.get(exchange, None)

    def get_name_from_symbol(self, symb):
        """
        Get the code of a money using its symbol.

        Uses the money_symbol.csv file.

        :param symb: Symbol of the money. ie. € or £
        :type symb: str
        :return: Code of the currency, ie. EUR or GBP
        :rtype: str
        """
        search = self.df_symbols_to_name.loc[self.df_symbols_to_name.symbol == symb, "name"]
        try:
            return search.iloc[0]
        except IndexError:
            return None

    def convert_price(self, price, symb, money_to="EUR", use_proxy=True):
        """
        Convert a price into a given currency.

        Uses request when necessary.
        :param use_proxy: True to use proxy, False otherwise
        :param price: amount to convert
        :type price: float or int
        :param symb: symbol of the currency in which the price is given.
        :type symb: str
        :param money_to: code of the currency in which the price should be converted.
        :type money_to: str
        :return: price in currency 'money_to'
        :rtype int
        """
        money_from = self.get_name_from_symbol(symb)
        if money_from is None:
            logger.warning(f"Unknown currency '{symb}'")
            return None
        exchange_rate = self.get_exchange_rate(money_from=money_from, money_to=money_to, use_proxy=use_proxy)
        if exchange_rate is not None:
            return self.round(price * exchange_rate)
        else:
            return None

    @staticmethod
    def round(n, decimals=0):
        """Convert a float to int, approx. by closes int."""
        multiplier = 10 ** decimals
        return int(math.floor(n * multiplier + 0.5) / multiplier)

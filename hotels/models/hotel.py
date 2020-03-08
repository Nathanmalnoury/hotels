import os

from hotels.conf_reader import ConfReader


class Hotel:
    conf_reader = ConfReader()
    conf = conf_reader.get("conf.ini")
    root_url = os.path.dirname(conf["TRIP_ADVISOR"]["base_url"])

    def __init__(self, name, rating, price, currency, detail_url):
        self.is_complete = all([name, rating, price, detail_url])
        self.name = name
        self.rating = rating
        self.price = price
        self.currency = currency
        self.detail_url = Hotel.root_url + detail_url

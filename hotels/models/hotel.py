import os

from hotels.utils.conf import Conf


class Hotel:
    root_url = os.path.dirname(Conf()["TRIP_ADVISOR"]["base_url"])

    def __init__(self, name, rating, price, currency, detail_url, needs_root=True):
        self.is_complete = all([name, rating, price, detail_url])
        self.name = name
        self.rating = rating
        self.price = price
        self.currency = currency
        self.detail_url = Hotel.root_url + detail_url if needs_root else detail_url

    @staticmethod
    def from_json(list_of_dict):
        list_hotels = []
        for hotel in list_of_dict:
            list_hotels.append(
                Hotel(
                    name=hotel["name"],
                    rating=hotel["rating"],
                    price=hotel["price"],
                    currency=hotel["currency"],
                    detail_url=hotel["detail_url"],
                    needs_root=False,
                )
            )
        return list_hotels

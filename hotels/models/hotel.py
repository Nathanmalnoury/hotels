"""Implement class Hotel."""
import os

from hotels.utils.conf import Conf


class Hotel:
    """Store hotel information."""

    root_url = os.path.dirname(Conf()["TRIP_ADVISOR"]["base_url"])

    def __init__(self, name, rating, price, currency, detail_url, needs_root=True):
        """
        Initialise Hotel object.

        :param name: Name of Hotel
        :param rating: Rating of Hotel
        :param price: Price of one night at the Hotel
        :param currency: Currency in which the price is given
        :param detail_url: Url to the detailed page of the Hotel
        :param needs_root: If the url needs the start of the url 'https://tripadvisor.co.uk' or not
        """
        self.is_complete = all([name, rating, price, detail_url])
        self.name = name
        self.rating = rating
        self.price = price
        self.currency = currency
        self.detail_url = Hotel.root_url + detail_url if needs_root else detail_url

    @staticmethod
    def from_json(list_of_dict):
        """
        Transform a list of dict from a json into a list off Hotel.

        :param list_of_dict: list of hotels read from json
        :type list_of_dict: list[dict]
        :return: list of Hotels
        :rtype: list[Hotel]
        """
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

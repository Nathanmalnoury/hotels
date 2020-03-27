"""Implement class Hotel."""
import json
import os

from hotels.utils.conf import Conf


class Hotel(object):
    """Store hotel information."""

    root_url = os.path.dirname(Conf()["TRIP_ADVISOR"]["base_url"])

    def __init__(self, name, rating, votes, price, currency, commodities, detail_url, needs_root=True):
        """
        Initialise Hotel object.

        :param commodities: list of Hotel
        :param votes: number pf votes
        :param name: Name of Hotel
        :param rating: Rating of Hotel
        :param price: Price of one night at the Hotel
        :param currency: Currency in which the price is given
        :param detail_url: Url to the detailed page of the Hotel
        :param needs_root: If the url needs the start of the url 'https://tripadvisor.co.uk' or not
        """
        self.commodities = commodities
        self.votes = votes
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
                    votes=hotel["votes"],
                    price=hotel["price"],
                    currency=hotel["currency"],
                    commodities=hotel["commodities"],
                    detail_url=hotel["detail_url"],
                    needs_root=False,
                )
            )
        return list_hotels

    def to_json(self):
        """
        Transform a Hotel object into a json-formatted string.
        :return: str
        """
        return json.dumps(
            obj=self.to_dict(),
            indent=2,
        )

    @staticmethod
    def list_to_json(list_of_hotels):
        """
        Transform a list of hotels in a json formatted string.
        :param list_of_hotels:
        :return: str
        """
        list_dict = [hotel.to_dict() for hotel in list_of_hotels]
        return json.dumps(
            obj=list_dict,
            indent=2,
        )

    def to_dict(self):
        """
        Return a Hotel object as a dict.
        :return: dict
        """
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "rating": self.rating,
            "votes": self.votes,
            "commodities": self.commodities,
            "detail_url": self.detail_url,
        }

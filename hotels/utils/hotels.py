"""Useful functions for managing excel files."""
import logging

import pandas as pd

from hotels.models.hotel import Hotel

logger = logging.getLogger("Hotels")


def save_as_excel(list_of_hotels, path_to_file):
    """
    Save a list of hotel as Excel document.

    :param list_of_hotels: list of Hotels to save
    :type list_of_hotels: list[Hotel]
    :param path_to_file: path to write the excel
    :type path_to_file: str
    :return: None
    """
    list_of_dicts = [hotel.to_dict() for hotel in list_of_hotels]
    df = pd.DataFrame(list_of_dicts)
    df.to_excel(path_to_file, index=False)
    logger.debug("Excel written")


def excel_to_hotels(path):
    """
    Get hotels from an excel file.

    :param path: path to excel file
    :type path: str
    :return: list of hotels
    :rtype list[Hotel]
    """
    df = pd.read_excel(path, index_col=0)
    list_hotels = []
    for i, data in df.iterrows():
        name = data["name"] if not pd.isna(data["name"]) else None
        rating = data["rating"] if not pd.isna(data["rating"]) else None
        votes = data["votes"] if not pd.isna(data["votes"]) else None
        commodities = data["commodities"] if not pd.isna(data["commodities"]) else None
        price = data["price"] if not pd.isna(data["price"]) else None
        currency = data["currency"] if not pd.isna(data["currency"]) else None
        detail_url = data["detail_url"] if not pd.isna(data["detail_url"]) else None

        list_hotels.append(
            Hotel(
                name=name,
                rating=rating,
                votes=votes,
                price=price,
                currency=currency,
                commodities=commodities,
                detail_url=detail_url,
                needs_root=False,
            )
        )
    return list_hotels


def get_incomplete_hotel(list_hotels):
    """
    Get incomplete hotels.

    :param list_hotels: list of hotels
    :type list_hotels: list[Hotel]
    :return: list of incomplete hotels
    :rtype: list[Hotel]
    """
    incomplete = []
    for hotel in list_hotels:
        if not hotel.is_complete:
            incomplete.append(hotel)
    return incomplete

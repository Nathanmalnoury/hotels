import logging

import pandas as pd

from hotels.models.hotel import Hotel

logger = logging.getLogger("Hotels")


def save_as_excel(list_of_hotels, path_to_file):
    list_of_dicts = [hotel.__dict__ for hotel in list_of_hotels]
    df = pd.DataFrame(list_of_dicts)
    df.to_excel(path_to_file)
    logger.debug("Excel written")


def excel_to_hotels(path):
    df = pd.read_excel(path, index_col=0)
    list_hotels = []
    for i, data in df.iterrows():
        name = data["name"] if not pd.isna(data["name"]) else None
        rating = data["rating"] if not pd.isna(data["rating"]) else None
        price = data["price"] if not pd.isna(data["price"]) else None
        currency = data["currency"] if not pd.isna(data["currency"]) else None
        detail_url = data["detail_url"] if not pd.isna(data["detail_url"]) else None

        list_hotels.append(
            Hotel(
                name=name,
                rating=rating,
                price=price,
                currency=currency,
                detail_url=detail_url,
                needs_root=False,
            )
        )
    return list_hotels


def get_incomplete_hotel(list_hotels):
    incomplete = []
    for hotel in list_hotels:
        if not hotel.is_complete:
            incomplete.append(hotel)
    return incomplete

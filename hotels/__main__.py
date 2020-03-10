#! /usr/bin/python3
import logging

from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils import save_as_excel, init

logger = logging.getLogger("Hotels")


def get_hotels_save_as_excel(url, path_excel):
    logger.info("Scrapping starts.")
    hotels = TripAdvisorScrapper.crawler(base_url=url)
    save_as_excel(hotels, path_excel)
    logger.info("Created Excel file, path: {}".format(path_excel))
    return hotels


if __name__ == '__main__':
    conf = init()
    # hotels_found = get_hotels_save_as_excel(
    #     conf["TRIP_ADVISOR"]["base_url"],
    #     conf["TRIP_ADVISOR"]["excel_path"]
    # )

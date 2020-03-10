import json
import logging
import os
import time

from hotels.utils.conf_reader import ConfReader
from hotels.parsers.hotel_parser import HotelParser
from hotels.parsers.page_parser import PageParser
from hotels.scrappers.scrapper import Scrapper
from hotels.utils.hotels import get_incomplete_hotel

logger = logging.getLogger("Hotels")


class TripAdvisorScrapper(Scrapper):
    def __init__(self, url, proxies=True):
        super().__init__(url, proxies)
        self.root_url = os.path.dirname(url)

    def get_page_info(self):
        card = self.soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        if card is not None:
            return PageParser(str(card.prettify())).get_info()
        else:
            return None

    def hotels_info(self):
        cards = self.soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(HotelParser(str(hotel_card.prettify())).parser())

        return info

    def process_one_page(self):
        start = time.time()
        self.load_soup(use_proxy=True)
        hotels = self.hotels_info()
        elapsed_time = time.time() - start
        logger.info(f"Process one page in {elapsed_time:.2f} s.")
        next_info = self.get_page_info()
        if next_info is not None:
            return dict([("hotels", hotels)], **next_info)
        else:
            return {"hotels": hotels}

    def process_last_page(self):
        start = time.time()
        self.load_soup(use_proxy=True)
        hotels = self.hotels_info()
        elapsed_time = time.time() - start
        logger.info(f"Process one page in {elapsed_time:.2f} s.")
        return {
            "hotels": hotels
        }

    @staticmethod
    def _get_save_dir():
        conf = ConfReader.get("conf.ini")
        return conf["TRIP_ADVISOR"]["save_dir"]

    @staticmethod
    def save_updates(data, page):
        """

        :param data: data to save
        :type data: dict
        :param page: page number, for file name
        :type page: int
        :return: None
        """
        logger.debug("Saving hotels")
        path = os.path.join(TripAdvisorScrapper._get_save_dir(), f"save_page_{page}.json")
        data["hotels"] = [h.__dict__ for h in data["hotels"]]

        with open(path, "w+") as f:
            json.dump(data, f)
        logger.info(f"Saved data up until page {page}")

    @staticmethod
    def roll_back_from_save(page):
        """

        :param page: page number to retrieve json file with
        :type page: int
        :return: data
        :rtype: dict
        """
        logger.info("Getting hotels from save file.")
        path = os.path.join(TripAdvisorScrapper._get_save_dir(), f"save_page_{page}.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data

    @staticmethod
    def crawler(base_url, data=None):
        if data is not None:
            hotels = data["hotels"]
        else:
            hotels = []

        next_url = "undefined"
        url = base_url
        logger.info("Crawling starts")

        while next_url is not None:
            scrapper = TripAdvisorScrapper(url)
            data = scrapper.process_one_page()

            hotels += data.get("hotels")
            current_page = data.get("current_page")
            page_max = data.get("total_page")
            next_url = data.get("next_link")

            TripAdvisorScrapper.save_updates(data, current_page)
            logger.info(f"Crawled Page {current_page}/{page_max}. Url : '{url}'")
            if next_url is None:
                break
            else:
                url = scrapper.root_url + next_url

            logger.info(f"Current number of hotels found : {len(hotels)}, "
                        f"number of hotels missing information: {len(get_incomplete_hotel(hotels))}")

        return hotels

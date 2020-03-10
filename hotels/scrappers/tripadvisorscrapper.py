import json
import logging
import os
import time

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
    def save_updates(data, page):
        logger.debug("Saving hotels")
        dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(dir_abs_path))
        path = os.path.join(root_path, "saves", f"save_page_{page}.json")
        data["hotels"] = [h.__dict__ for h in data["hotels"]]
        with open(path, "w+") as f:
            json.dump(data, f)
        logger.info(f"Saved data up until {page}")

    @staticmethod
    def roll_back_from_save(page_num):
        logger.info("Getting hotels from save file.")
        dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(dir_abs_path))
        path = os.path.join(root_path, "saves", f"save_page_{page_num}.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data

    @staticmethod
    def crawler(base_url):
        hotels = []
        next_url = "undefined"
        url = base_url
        logger.info("Crawling starts")

        while next_url is not None:
            scrapper = TripAdvisorScrapper(url)
            root_url = scrapper.root_url

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
                url = root_url + next_url

            logger.info(f"Current number of hotels found : {len(hotels)}, "
                        f"Hotels missing information: {len(get_incomplete_hotel(hotels))}")

        return hotels

"""Scrapper for TripAdvisor

This module is responsible for orchestrating the scrapping.
It uses the parsers and the WebDriver classes to load the page, change the currency and finally get the results.
It supports saving the data, as well as getting the data back from previous saves.
"""
import json
import logging
import os
import time

from bs4 import BeautifulSoup

from hotels.parsers.hotel_parser import HotelParser
from hotels.parsers.page_parser import PageParser
from hotels.scrappers.scrapper import Scrapper
from hotels.scrappers.web_driver import WebDriverTripAdvisor
from hotels.utils.conf import Conf

logger = logging.getLogger("Hotels")


class TripAdvisorScrapper(Scrapper):
    def __init__(self, url, headless=True):
        super().__init__(url)
        self.root_url = os.path.dirname(url)
        self.headless = headless

    def get_page_info(self):
        soup = BeautifulSoup(self.page, "html.parser")
        card = soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        if card is not None:
            return PageParser(str(card.prettify())).get_info()
        else:
            logger.error("no footer found.")
            logger.debug(soup)
            return None

    def hotels_info(self):
        soup = BeautifulSoup(self.page, "html.parser")
        cards = soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(HotelParser(str(hotel_card.prettify())).parser())

        return info

    @staticmethod
    def _get_save_dir():
        conf = Conf()
        return conf["TRIP_ADVISOR"]["save_dir"]

    @staticmethod
    def save_updates(data, page):
        """

        :param data: data to save
        :type data: dict
        :param page: page number, for file name
        :type page: int or None
        :return: None
        """
        path = os.path.join(TripAdvisorScrapper._get_save_dir(), f"save_page_{page}.json")
        data["hotels"] = [h.__dict__ for h in data["hotels"]]

        with open(path, "w+") as f:
            json.dump(data, f)

        logger.info(f"Saved data up until page {page}.")

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
    def crawler(first_url, data=None, headless=True):
        if data is not None:
            hotels = data["hotels"]
        else:
            hotels = []

        next_url = first_url
        logger.debug("Crawling starts")
        times = []

        while next_url is not None:
            next_url, elapsed_time, current_page, page_max = TripAdvisorScrapper.process_one_page(next_url,
                                                                                                  headless,
                                                                                                  hotels)
            times.append(elapsed_time)
            TripAdvisorScrapper.compute_eta(times, page_max)
            if next_url is None:
                break
            
        return hotels

    @staticmethod
    def process_one_page(url, headless, hotels):
        scrapper = TripAdvisorScrapper(url, headless=headless)

        start = time.time()
        scrapper.page = WebDriverTripAdvisor.get(url=scrapper.url, headless=scrapper.headless)
        found_hotels = scrapper.hotels_info()
        next_info = scrapper.get_page_info()
        elapsed_time = time.time() - start

        hotels += found_hotels
        current_page = next_info.get("current_page")
        page_max = next_info.get("total_page")
        next_url = next_info.get("next_link", None)
        if next_url is not None:
            next_url = scrapper.root_url + next_url

        TripAdvisorScrapper.save_updates(dict([("hotels", hotels)], **next_info), current_page)

        logger.info(
            f"Scrapped Page {current_page}/{page_max} in {elapsed_time:.2f}s. "
            f"Found {len(found_hotels)} hotels, {len(hotels)} in total."
        )

        return next_url, elapsed_time, current_page, page_max

    @staticmethod
    def compute_eta(times, page_max):
        """
        :type times: list of float
        :type current_page: int
        :type page_max: int
        :return: None
        """
        page_done = len(times)
        total_elapsed_time = sum(times)
        mean_time = total_elapsed_time / page_done
        total_eta = page_max * mean_time
        eta_min = (total_eta - total_elapsed_time) / 60
        secs = int((eta_min - int(eta_min)) * 60)

        logger.info(f"ETA: {int(eta_min)}m{secs}s; Avg. time per page: {mean_time:.2f}s.")

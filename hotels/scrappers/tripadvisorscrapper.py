"""Scrapper for TripAdvisor.

This module is responsible for orchestrating the scrapping.
It uses the parsers and the WebDriver classes to load the page, change the currency and finally get the results.
It supports saving the data, as well as getting the data back from previous saves.
"""
import datetime
import json
import logging
import os
import time

from bs4 import BeautifulSoup

from hotels.models.hotel import Hotel
from hotels.parsers.hotel_parser import HotelParser
from hotels.parsers.page_parser import PageParser
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.scrapper import Scrapper
from hotels.scrappers.web_driver import WebDriverTripAdvisor
from hotels.utils.conf import Conf
from hotels.utils.misc import write_html_error

logger = logging.getLogger("Hotels")


class TripAdvisorScrapper(Scrapper):
    """Scrapped for TripAdvisor UK Hotel pages."""

    def __init__(self, url, headless=True):
        """
        Init.

        :param url: url to scrap.
        :param headless: Whether or not to show the user the browser.
        """
        super().__init__(url)
        self.root_url = os.path.dirname(url)
        self.headless = headless

    def get_page_info(self):
        """Get Page information using PageParser."""
        soup = BeautifulSoup(self.page, "html.parser")
        card = soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        if card is not None:
            return PageParser(str(card.prettify())).get_info()
        else:
            logger.error("no footer found.")
            write_html_error(self.page)
            return None

    def hotels_info(self):
        """Get hotels information using HotelParser."""
        soup = BeautifulSoup(self.page, "html.parser")
        cards = soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(HotelParser(str(hotel_card.prettify())).parser())

        return info

    @staticmethod
    def _get_save_dir():
        return Conf().get_path("TRIP_ADVISOR", "save_dir")

    @staticmethod
    def save_updates(data, page):
        """
        Save the current scrapped data.

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
        Get back the data scraped from a previous aborted crawl.

        :param page: page number to retrieve json file with
        :type page: int
        :return: data
        :rtype: dict
        """
        logger.info("Getting hotels from save file.")
        path = os.path.join(TripAdvisorScrapper._get_save_dir(), f"save_page_{page}.json")
        with open(path, "r") as f:
            data = json.load(f)
        hotels = data.get("hotels")
        if hotels is not None:
            hotels = Hotel.from_json(hotels)
        data["hotels"] = hotels
        return data

    @staticmethod
    def crawler(first_url, data=None, headless=True, use_proxy=True, timeout=300):
        """
        Crawls to all the next pages of a requested url.

        If first_url is the first page of the request, it crawls every hotels.

        :param use_proxy: Whether or not to use proxy.
        :param first_url: url
        :param timeout: timeout for loading the page.
        :type timeout: int
        :type first_url:url
        :param data: optionnal already scrapped data, from an aborted previous scrap.
        :type data: dict
        :param headless: whether or not to show the user the browser.
        :return: list of Hotel
        :rtype list[hotels.models.hotel.Hotel]:
        """
        if data is not None:
            hotels = data["hotels"]
        else:
            hotels = []

        next_url = first_url
        logger.debug("Crawling starts")
        times = []
        if use_proxy:
            proxy = ProxyPool().get_proxy()

        while next_url is not None:
            if not use_proxy:
                next_url, elapsed_time, current_page, page_max = TripAdvisorScrapper.process_one_page(
                    next_url, headless, hotels, proxy=None, timeout=timeout)
            else:
                while True:
                    try:
                        next_url, elapsed_time, current_page, page_max = TripAdvisorScrapper.process_one_page(
                            next_url, headless, hotels, proxy=proxy, timeout=timeout)
                        break
                    except Exception as e:
                        logger.debug(f"Get TripAdvisor page with proxy did not work: '{e.__class__}'")
                        logger.exception(e)
                        ProxyPool().remove_proxy(proxy)
                        proxy = ProxyPool().get_proxy()

            times.append(elapsed_time)
            TripAdvisorScrapper.compute_eta(times, page_max)
            if next_url is None:
                break

        return hotels

    @staticmethod
    def process_one_page(url, headless, hotels, proxy, timeout):
        """
        Get, Scrap and parse one page.

        :param timeout: timeout
        :type timeout:int
        :param use_proxy: Whether or not to use proxy
        :param url: url to process.
        :type url: str
        :param headless: whether or not to show the browser to the user.
        :type headless: bool
        :param hotels: list of previously parsed hotels.
        :type hotels: list[Hotel]
        :return: next_url, elapsed_time, current_page, page_max
        """
        scrapper = TripAdvisorScrapper(url, headless=headless)

        start = time.time()

        scrapper.page = WebDriverTripAdvisor.get(url=scrapper.url,
                                                 headless=scrapper.headless,
                                                 proxy=proxy,
                                                 timeout=timeout)

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
        Compute Estimated Time of Arrival for the crawler.

        :type times: list of float
        :type current_page: int
        :type page_max: int
        :return: None
        """
        page_done = len(times)
        total_elapsed_time = sum(times)
        mean_time = total_elapsed_time / page_done
        total_eta = page_max * mean_time
        eta_s = (total_eta - total_elapsed_time)
        eta_human_readable = str(datetime.timedelta(seconds=eta_s))
        mean_time_human_readable = str(datetime.timedelta(seconds=mean_time))

        logger.info(f"ETA: {eta_human_readable}; Avg. time per page: {mean_time_human_readable}s.")

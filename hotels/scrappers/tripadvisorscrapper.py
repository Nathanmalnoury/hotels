import json
import logging
import os
import time
from datetime import date

from bs4 import BeautifulSoup

from hotels.parsers.hotel_parser import HotelParser
from hotels.parsers.page_parser import PageParser
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.scrapper import Scrapper
from hotels.utils.conf_reader import ConfReader

logger = logging.getLogger("Hotels")


class TripAdvisorScrapper(Scrapper):
    def __init__(self, url, headless=True, load_timeout=200):
        super().__init__(url)
        self.root_url = os.path.dirname(url)
        self.headless = headless
        self.load_timeout = load_timeout

    def scrap(self):
        proxy_pool = ProxyPool.instance()
        while True:
            proxy = proxy_pool.get_proxy()
            driver = self.get_driver(proxy=proxy, headless=self.headless, load_timeout=self.load_timeout)

            try:
                driver.get(self.url)
                if self.page_is_empty(driver) or self.page_is_error(driver):
                    logger.debug("Empty page, or error page.")
                    driver.close()
                    proxy_pool.remove_proxy(proxy)
                    continue

                self.chrome_change_currency(driver)
                time.sleep(25)
                logger.debug(f"Request is a success, for page '{driver.title}'")
                self.page = driver.page_source
                driver.close()
                break

            except:
                driver.close()
                proxy_pool.remove_proxy(proxy)

    def get_page_info(self):
        soup = BeautifulSoup(self.page, "html.parser")
        card = soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        if card is not None:
            return PageParser(str(card.prettify())).get_info()
        else:
            return None

    def hotels_info(self):
        soup = BeautifulSoup(self.page, "html.parser")
        cards = soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(HotelParser(str(hotel_card.prettify())).parser())

        return info

    def process_one_page(self):
        start = time.time()
        self.scrap()
        hotels = self.hotels_info()
        elapsed_time = time.time() - start
        logger.info(f"Process one page in {elapsed_time:.2f} s.")
        next_info = self.get_page_info()
        if next_info is not None:
            return dict([("hotels", hotels)], **next_info)
        else:
            return {"hotels": hotels}

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
    def crawler(base_url, data=None, headless=True, load_timeout=200):
        if data is not None:
            hotels = data["hotels"]
        else:
            hotels = []

        next_url = "undefined"
        url = base_url
        logger.info("Crawling starts")

        while next_url is not None:
            scrapper = TripAdvisorScrapper(url, headless=headless, load_timeout=load_timeout)
            data = scrapper.process_one_page()

            hotels += data.get("hotels")
            current_page = data.get("current_page")
            page_max = data.get("total_page")
            next_url = data.get("next_link")

            data["hotels"] = hotels  # for saving all hotels

            TripAdvisorScrapper.save_updates(data, current_page)
            logger.info(f"Crawled Page {current_page}/{page_max}. Url : '{url}'")
            if next_url is None:
                break
            else:
                url = scrapper.root_url + next_url
        return hotels

    @staticmethod
    def chrome_change_currency(driver):
        try:
            time.sleep(5)
            driver.find_element_by_xpath("//div[@data-header='Currency']").click()
            time.sleep(15)
            euro = driver.find_element_by_xpath("//div[@class='currency_code' and text() = 'EUR']/parent::node()")
            euro.click()
            time.sleep(5)
            logger.info("Change currency, success.")
            return True

        except Exception as e:
            logger.warning("Change currency, fail.")
            return False

    @staticmethod
    def page_is_error(driver):
        err_detector = ["Privacy error", "error-information-button", "ERR_"]
        for err in err_detector:
            if err in driver.page_source:
                return True
        return False

    @staticmethod
    def page_is_empty(driver):
        page = driver.page_source
        if page == "<html><head></head><body></body></html>":
            return True
        elif page is None:
            return True
        elif not page:
            return True
        else:
            return False

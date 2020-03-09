import logging
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from hotels.proxy_pool import ProxyPool

logger = logging.getLogger("Hotels")


class Scrapper:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    timeout = 20

    def __init__(self, url, proxies=False):
        logger.info("Scrapper initialised with url `{}`".format(url))
        self.url = url
        self.page = None
        self.soup = None
        self.proxies = proxies
        self.proxy_pool = None

    def _request(self):
        """
        Make the request on the URL.

        Later to include anti-blocking policies.
        Populates the page attribute.
        :return: None
        """
        if not self.proxies:
            self.page = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        else:
            self._request_with_proxies()

    def load_soup(self, use_proxy=True):
        if not use_proxy:
            self._request()
            self.soup = BeautifulSoup(self.page.content, 'html.parser')

        else:
            self._request_with_proxies()
            self.soup = BeautifulSoup(self.page, 'html.parser')

    def get_html(self):
        return self.soup

    def _get_next_proxy(self):
        return next(self.proxy_pool)

    def _request_with_proxies(self):
        proxy_pool = ProxyPool.instance()
        while True:
            proxy = proxy_pool.get_proxy()
            logger.debug(f"using proxy {proxy}")

            try:
                chrome = self._get_driver_options(proxy)
                chrome.get(self.url)
                sleep(100)

                logger.debug("Got title :" + chrome.title)

                if self.page_is_empty(page=chrome.page_source) or self.page_is_error(chrome.page_source):
                    chrome.close()
                    raise Exception("chrome error page")

                self.page = chrome.page_source
                chrome.close()

                logger.info("Request is a success.")
                break

            except Exception as e:
                logger.error("Connection Error for proxy {}".format(proxy))
                logger.error(e)
                proxy_pool.remove_proxy(proxy)

    @staticmethod
    def _get_driver_options(proxy):
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server={proxy}')
        options.add_argument('--headless')

        chrome = webdriver.Chrome(chrome_options=options)
        chrome.set_page_load_timeout(200)  # Wait n sec before giving up on loading page
        chrome.set_window_size(width=1700, height=500)
        return chrome

    @staticmethod
    def page_is_empty(page):
        if page == "<html><head></head><body></body></html>":
            return True
        elif page is None:
            return True
        elif not page:
            return True
        else:
            return False

    @staticmethod
    def page_is_error(page):
        err_detector = ["Privacy error", "error-information-button", "ERR_"]
        for err in err_detector:
            if err in page:
                return True
        return False

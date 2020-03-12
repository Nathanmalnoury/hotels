import logging

import requests
from selenium import webdriver

from hotels.proxy_pool import ProxyPool

logger = logging.getLogger("Hotels")


class Scrapper:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    timeout = 20

    def __init__(self, url):
        logger.info(f"Scrapper initialised with url '{url}'")
        self.url = url
        self.page = None
        self.soup = None

    def simple_request(self, use_proxy=False):
        parameters = {
            "url": self.url,
            "headers": self.headers,
            "timeout": self.timeout,
        }

        if use_proxy:
            proxy = ProxyPool.instance().get_proxy()
            parameters["proxies"] = {'http': proxy, 'https': proxy}

        self.page = requests.get(**parameters)
        return self.page

    @staticmethod
    def get_driver(proxy=None, headless=True, load_timeout=200):
        options = webdriver.ChromeOptions()
        if proxy is not None:
            options.add_argument(f'--proxy-server={proxy}')
        if headless:
            options.add_argument('--headless')

        chrome = webdriver.Chrome(chrome_options=options)
        chrome.set_page_load_timeout(load_timeout)  # Wait n sec before giving up on loading page
        chrome.set_window_size(width=1700, height=500)
        return chrome

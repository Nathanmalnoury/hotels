"""General Scrapper Class."""
import logging

import requests

from hotels.proxy_pool import ProxyPool

logger = logging.getLogger("Hotels")


class Scrapper:
    """Scrapper capable of simple requests (No webdriver support.)."""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    timeout = 20

    def __init__(self, url):
        """
        Init.

        :param url: url to Scrap or get
        """
        logger.debug(f"Scrapper initialised with url '{url}'")
        self.url = url
        self.page = None
        self.soup = None

    def simple_request(self, use_proxy=False):
        """
        Request a url, using a proxy or not.

        :param use_proxy: Bool, to use proxy or not
        :type use_proxy: bool
        :return: Response
        """
        parameters = {
            "url": self.url,
            "headers": self.headers,
            "timeout": self.timeout,
        }
        if not use_proxy:
            self.page = requests.get(**parameters)
        else:
            while True:
                proxy = ProxyPool().get_proxy()
                logger.debug(proxy)
                parameters["proxies"] = {'http': proxy, 'https': proxy}
                try:
                    self.page = requests.get(**parameters)
                    break
                except Exception as e:
                    logger.warning(e)
                    ProxyPool().remove_proxy(proxy)
                    continue

        logger.debug("request made.")
        return self.page

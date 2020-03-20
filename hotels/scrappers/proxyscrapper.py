"""Scrapper for proxy website https://free-proxy-list.net/ ."""
import logging

from lxml.html import fromstring

from hotels.scrappers.scrapper import Scrapper

logger = logging.getLogger("Hotels")


class ProxyScrapper(Scrapper):
    """Scrapper for proxies."""

    def __init__(self, url):
        """Initialise a ProxyScrapper instance."""
        super().__init__(url)
        self.list_proxies = []

    def get_proxies(self, use_proxy=False):
        """Get proxies, if proxies has not already been scrapped."""
        if not self.list_proxies:
            self._request_proxies(use_proxy)
        return self.list_proxies

    def _request_proxies(self, use_proxy=False):
        """Scrap proxies from website."""
        self.simple_request(use_proxy=use_proxy)
        parser = fromstring(self.page.text)
        proxies = set()
        dict_tmp = {}
        for i in parser.xpath('//tbody/tr'):  # Access the table.
            if i.xpath('.//td[7][contains(text(),"yes")]'):  # Only select https proxies
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                # Grab the time since last check.
                dict_tmp[proxy] = self.parse_time(i.xpath('.//td[8]/text()')[0])
                proxies.add(proxy)

        list_proxies = list(proxies)
        list_proxies.sort(key=lambda prox: dict_tmp[prox])  # sort proxies by most recent check.

        logger.debug(f"found {len(proxies)} proxies.")
        self.list_proxies = list_proxies

    @staticmethod
    def parse_time(time_sentence):
        """Parse time from website, and make the machine-readable."""
        l_ = time_sentence.split()
        unit = l_[1]
        if unit in ["seconds", "second"]:
            return int(l_[0])
        elif unit in ["minutes", "minute"]:
            return int(l_[0]) * 60
        else:
            logger.error(f"unknown unit, {unit}")
            raise Exception("unknown time unit")

import logging

from lxml.html import fromstring

from hotels.scrappers.scrapper import Scrapper

logger = logging.getLogger("Hotels")


class ProxyScrapper(Scrapper):
    def __init__(self, url):
        super().__init__(url)

    def get_proxies(self):
        parser = fromstring(self.page.text)
        proxies = set()
        dict_tmp = {}
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                dict_tmp[proxy] = self.parse_time(i.xpath('.//td[8]/text()')[0])
                proxies.add(proxy)

        list_proxies = list(proxies)
        list_proxies.sort(key=lambda prox: dict_tmp[prox])

        logger.info(f"found {len(proxies)} proxies.")
        return list_proxies

    @staticmethod
    def parse_time(time_sentence):
        l_ = time_sentence.split()
        unit = l_[1]
        if unit in ["seconds", "second"]:
            return int(l_[0])
        elif unit in ["minutes", "minute"]:
            return int(l_[0]) * 60
        else:
            logger.error(f"unknown unit, {unit}")
            raise Exception("unknown time unit")

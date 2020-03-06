from lxml.html import fromstring

from hotels.scrappers.scrapper import Scrapper


class ProxyScrapper(Scrapper):
    def __init__(self, url):
        super().__init__(url)

    def get_proxies(self):
        parser = fromstring(self.page.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)

        print(f"found {len(proxies)} proxies.")
        return proxies

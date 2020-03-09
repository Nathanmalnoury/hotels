from hotels.scrappers.scrapper import Scrapper


class DetailsScrapper(Scrapper):
    def __init__(self, url, proxies=True):
        super().__init__(url, proxies=proxies)

    def get_price_div(self):
        return self.soup.find("div", {"class": "premium_offers_area offers"})
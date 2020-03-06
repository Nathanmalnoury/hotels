import re

from bs4 import BeautifulSoup

from hotels.scrappers.scrapper import Scrapper


class TripAdvisorScrapper(Scrapper):
    def __init__(self, url):
        super().__init__(url)

    def get_page_count(self):
        card = self.soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        print(card)
        return card

    def get_next_page(self):
        pass

    def hotels_info(self):
        print(self.soup)
        cards = self.soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(self.scrap_one_hotel(hotel_card.prettify))

        return info[0]

    @staticmethod
    def scrap_one_hotel(hotel_card):
        regexp_hotel_name = re.compile(r"<a.*property_title.*</a>")

        return hotel_card



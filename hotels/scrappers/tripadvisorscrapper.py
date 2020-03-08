import json
import os
import time

from hotels.parsers.hotel_parser import HotelParser
from hotels.parsers.page_parser import PageParser
from hotels.scrappers.scrapper import Scrapper


class TripAdvisorScrapper(Scrapper):
    def __init__(self, url):
        super().__init__(url)
        self.root_url = os.path.dirname(url)
        print(self.root_url)

    def get_page_info(self):
        card = self.soup.find("div", {"class": "unified ui_pagination standard_pagination ui_section listFooter"})
        if card is not None:
            return PageParser(str(card.prettify())).get_info()
        else:
            return None

    def hotels_info(self):
        cards = self.soup.find_all("div", {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
        info = []
        for hotel_card in cards:
            if hotel_card is not None:
                info.append(HotelParser(str(hotel_card.prettify())).parser())

        return info

    def process_one_page(self):
        start = time.time()
        self.load_soup(use_proxy=True)
        hotels = self.hotels_info()
        print("Process one page in {:.2f} s.".format(time.time() - start))
        next_info = self.get_page_info()
        if next_info is not None:
            return dict([("hotels", hotels)], **next_info)
        else:
            return {"hotels": hotels}

    def process_last_page(self):
        start = time.time()
        self.load_soup(use_proxy=True)
        hotels = self.hotels_info()
        print("Process one page in {:.2f} s.".format(time.time() - start))
        return {
            "hotels": hotels
        }

    @staticmethod
    def save_updates(hotels, page):
        dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(dir_abs_path))
        path = os.path.join(root_path, "saves", "save_page_{}.json".format(page))
        print(hotels)
        hotels_serialized = [h.__dict__ for h in hotels]
        with open(path, "w+") as f:
            json.dump(hotels_serialized, f)

    @staticmethod
    def crawler(base_url):
        hotels = []
        next_url = "undefined"
        url = base_url
        print("Crawling starts")

        while next_url is not None:
            scrapper = TripAdvisorScrapper(url)
            root_url = scrapper.root_url

            data = scrapper.process_one_page()

            hotels += data.get("hotels")
            current_page = data.get("current_page")
            page_max = data.get("total_page")
            next_url = data.get("next_link")

            TripAdvisorScrapper.save_updates(hotels, current_page)
            print("Crawled Page {}/{}. Url : '{}'".format(current_page, page_max, url))

            url = root_url + next_url
            print(f"Current number of hotels found : {len(hotels)}")

        return hotels

from email.parser import Parser


class HotelDetailsParser(Parser):
    def __init__(self):
        super().__init__()

    def get_price(self):
        test = self.soup.find("div", {"class": "premium_offers_area offers"})
        print(test)

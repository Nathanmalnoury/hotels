import re

from hotels.currency_exchanger import CurrencyExchanger
from hotels.models.hotel import Hotel


class HotelParser:
    def __init__(self, str_hotel):
        self.str_hotel = str_hotel
        self.converter = CurrencyExchanger(token="d6e953f1f00fc9e91339")

    def parser(self):
        name = self.get_hotel_name()
        rating = self.get_rating()
        price, currency = self.get_price()
        detail_url = self.get_detail_url()

        return Hotel(name=name, rating=rating, price=price, currency=currency, detail_url=detail_url)

    def get_hotel_name(self):
        try:
            tag_matcher = re.compile(r'<a class="property_title prominent"[\w\W]*?</a>')
            tag = tag_matcher.search(self.str_hotel).group()
            lines = tag.split("\n")
            return lines[1].strip()
        except:
            print("Hotel name not found")
            return None

    def get_rating(self):
        try:
            tag_matcher = re.compile(r'<.*data-clicksource="BubbleRating"[\w\W]+?</a>')
            tag = tag_matcher.search(self.str_hotel).group()
            rating_matcher = re.compile(r'".*?bubbles"')
            ratings = rating_matcher.search(tag).group().split()
            first_number = ratings[0][1:]  # matches on '"4.5', we have to remove "
            last_number = ratings[2]
            return "{}/{}".format(first_number, last_number)
        except:
            print("Hotel rating not found")
            return None

    def get_price(self):
        tag_matcher = re.compile(r'<div class="price autoResize"[\w\W]+?</div>')
        for tag in re.finditer(tag_matcher, self.str_hotel):
            try:
                lines = tag.group().split("\n")
                if len(lines) == 3:
                    price = lines[1].strip()
                    price_finder = re.compile(r'([\d,. ])+')
                    amount = price_finder.search(price).group()
                    symbol = price.replace(amount, "").strip()

                    amount = amount.strip()
                    amount = self.clean_amount(amount)

                    print("amount: {}, in currency: {}".format(amount, symbol))
                    try:

                        amount = self.converter.convert_price(price=amount, symb=symbol)
                        symbol = "EUR"
                        print("In euro : {}".format(amount))

                    except Exception as e:
                        print("Error while converting price")
                        print(e)
                        pass

                    return amount, symbol

            except Exception as e:
                print("Error while parsing the price")
                print(e.__class__, e)

        print("No Price found !")
        return None, None

    def get_detail_url(self):
        try:
            tag_matcher = re.compile(r'<div class="photo-wrapper">[\w\W]*?href=".*"')
            tag = tag_matcher.search(self.str_hotel).group()
            url_matcher = re.compile(r'"/.+?.html"')
            link = url_matcher.search(tag).group()
            link = link.split("\"")[1]
            return link
        except:
            return None

    @staticmethod
    def clean_amount(amount):
        # original amount "13,082.63" or "13 082.36"
        # converts to float: 13082.63
        amount = amount.replace(",", "")
        amount = amount.replace(" ", "")
        return float(amount)

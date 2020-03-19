import logging
import re

from hotels import Conf
from hotels.currency_exchanger import CurrencyExchanger
from hotels.models.hotel import Hotel

logger = logging.getLogger("Hotels")


class HotelParser:
    wanted_currency_name = Conf()["TRIP_ADVISOR"]["currency_wanted_name"]

    def __init__(self, str_hotel):
        self.str_hotel = str_hotel
        self.converter = CurrencyExchanger()

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
            logger.warning("Hotel name not found")
            return None

    def get_rating(self):
        try:
            tag_matcher = re.compile(r'<.*data-clicksource="BubbleRating"[\w\W]+?</a>')
            tag = tag_matcher.search(self.str_hotel).group()
            rating_matcher = re.compile(r'".*?bubbles"')
            ratings = rating_matcher.search(tag).group().split()
            first_number = ratings[0][1:]  # matches on '"4.5', we have to remove "
            last_number = ratings[2]
            return f"{first_number}/{last_number}"
        except:
            votes = self.get_votes()
            if votes is not None and votes == 0:
                return "No votes"
            else:
                logger.warning("could not find rating")
                return None

    def get_price(self):
        tag_matcher = re.compile(r'<div .* data-sizegroup="mini-meta-price"[\w\W]+?</div>')
        for tag in re.finditer(tag_matcher, self.str_hotel):
            try:
                lines = tag.group().split("\n")
                if len(lines) == 3:
                    return self.price_parser(lines)

            except Exception as e:
                logger.error("Error while parsing the price:\n")
                logger.error(e)

        if self.no_price_available():
            logger.debug("No price available for this hotel.")
            return "No price available", " "

        logger.error("No match found for tag_matcher")
        logger.debug(self.str_hotel)

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
            logger.error("Get detail url failed.")
            return None

    @staticmethod
    def clean_amount(amount):
        # original amount "13,082.63" or "13 082.36"
        # converts to float: 13082.63
        amount = amount.replace(",", "")
        amount = amount.replace(" ", "")
        return float(amount)

    def get_votes(self):
        matcher = re.compile(r'<a.*"review_count[\w\W]+?</a>')
        try:
            tag = matcher.search(self.str_hotel).group()
            count = tag.split("\n")
            count = count[1]
            count = count.split()
            return int(count[0])

        except:
            logger.warning("No review count found")
            return None

    def no_price_available(self):
        matcher = re.compile(r'<div class="note">\n\s+Contact accommodation for availability.')
        match = matcher.search(self.str_hotel)
        if match.group() is not None:
            return True
        return False

    def price_parser(self, lines):
        price = lines[1].strip()
        price_finder = re.compile(r'([\d,. ])+')
        amount = price_finder.search(price).group()
        symbol = price.replace(amount, "").strip()

        amount = amount.strip()
        amount = self.clean_amount(amount)
        try:

            amount = self.converter.convert_price(price=amount, symb=symbol, money_to=HotelParser.wanted_currency_name)
            symbol = HotelParser.wanted_currency_name

        except Exception as e:
            logger.error("Error while converting price")
            logger.error(e)
            pass

        return amount, symbol

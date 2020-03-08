import re

from hotels.models.hotel import Hotel


class HotelParser:
    def __init__(self, str_hotel):
        self.str_hotel = str_hotel

    def parser(self):
        try:
            name = self.get_hotel_name()
            rating = self.get_rating()
            price = self.get_price()
            detail_url = self.get_detail_url()
            return Hotel(name=name, rating=rating, price=price, detail_url=detail_url)

        except Exception as e:
            print(e)

        return None

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

                    print("amount: {}, in currency: {}".format(amount, symbol))
                    # TODO convert money to euros
                    return amount

            except Exception as e:
                print(e)

        print("No Price found !")
        return None

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
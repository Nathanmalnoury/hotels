#! /usr/bin/python3
from hotels.scrappers.details_scrapper import DetailsScrapper
from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils import save_as_excel, init

conf = init()


def get_hotels_save_as_excel(url):
    print("Scrapping starts.")
    hotels = TripAdvisorScrapper.crawler(base_url=url)
    path_excel = "/home/nathan/Desktop/test.xlsx"
    save_as_excel(hotels, path_excel)
    print("Created Excel file, path: {}".format(path_excel))
    return hotels


if __name__ == '__main__':
    hotels_found = get_hotels_save_as_excel(conf["TRIP_ADVISOR"]["base_url"])
    # url_test = "https://www.tripadvisor.co.uk/Hotel_Review-g187162-d197312-Reviews-Hotel_Mercure_Nancy_Centre_Gare-Nancy_Meurthe_et_Moselle_Grand_Est.html"
    # ds = DetailsScrapper(url="http://www.whatismyproxy.com/")
    # ds.load_soup()
    # print(type(ds.page))

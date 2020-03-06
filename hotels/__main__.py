#! /usr/bin/python3
from hotels.conf_reader import ConfReader
from hotels.scrappers.proxyscrapper import ProxyScrapper
from hotels.scrappers.scrapper import ProxyPool
from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper

conf_reader = ConfReader()
conf = conf_reader.get("conf.ini")

print("Searching proxies.")
proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])
proxy_scrapper.load_soup(use_proxy=False)
proxies = proxy_scrapper.get_proxies()
print("Creating a proxy pool.")
ProxyPool.initialize(proxies=proxies)

print("Scrapping Base URL.")
scrp = TripAdvisorScrapper(url=conf["TRIP_ADVISOR"]["base_url"])
scrp.load_soup()

print(scrp.hotels_info())

# scrapper = PageScrapper()
# scrapper.load_soup()
# print(scrapper.get_list_hotels())

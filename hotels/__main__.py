#! /usr/bin/python3
from hotels.conf_reader import ConfReader
from hotels.scrappers.proxyscrapper import ProxyScrapper
from hotels.scrappers.scrapper import ProxyPool
from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils import save_as_excel

conf_reader = ConfReader()
conf = conf_reader.get("conf.ini")

print("Searching proxies.")
proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])
proxy_scrapper.load_soup(use_proxy=False)
proxies = proxy_scrapper.get_proxies()
print("Creating a proxy pool.")
ProxyPool.initialize(proxies=proxies)

print("Scrapping starts.")
data = TripAdvisorScrapper.crawler(base_url=conf["TRIP_ADVISOR"]["base_url"])
save_as_excel(data, "/home/nathan/Desktop/test.xlsx")
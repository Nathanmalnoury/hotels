"""Functions useful for the rest of the algorithm."""
import logging
import os
import time
from datetime import datetime
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup

from hotels.currency_exchanger import CurrencyExchanger
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper
from hotels.utils.conf import Conf
from hotels.utils.custom_formatter import CustomFormatterStream, CustomFormatterFile

logger = logging.getLogger("Hotels")


def init():
    """
    Initialize the classes needed for the software.

    ie. ProxyPool instance and a Currency exchanger instance.

    :return: conf
    :rtype hotels.utils.conf.Conf:
    """
    conf = Conf()

    logger.debug("Searching proxies.")
    proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])

    logger.debug("Creating a proxy pool.")
    ProxyPool(proxy_scrapper.get_proxies())
    s = time.time()
    # test_proxies(8)
    logger.info(f"Tested proxies in {time.time() - s:.2f}s. Remaining: {len(ProxyPool().proxies)} proxies")
    logger.debug("Creating a currency exchanger.")
    CurrencyExchanger()
    return conf


def set_logger():
    """Set up logger for stream and file logs."""
    logger_ = logging.getLogger('Hotels')
    logger_.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    path_conf = os.path.join(Conf().get_path("TRIP_ADVISOR", "log_dir"), "hotels.log")

    if not os.path.isfile(path=path_conf):
        # creates the file if it does not exist
        with open(path_conf, "w+"):
            pass

    fh = logging.FileHandler(path_conf, mode="a+", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(CustomFormatterFile())

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatterStream())

    # add the handlers to the logger
    logger_.addHandler(fh)
    logger_.addHandler(ch)


def write_html_error(html_page):
    """Take an html and write it to the log directory."""
    now = datetime.now().strftime("%d-%m-%H:%M:%S")
    path_log = Conf().get_path("TRIP_ADVISOR", "log_dir")
    path = os.path.join(path_log, f"error_{now}.html")

    with open(path, "w+") as f:
        f.write(html_page)

    logger.debug(f"html error written in {path}")


def test_proxies(num_worker_threads=8):
    p = ProxyPool()

    def test_proxy(proxy):
        try:
            r = requests.get(
                url="https://www.google.com/",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                },
                proxies={'http': proxy, 'https': proxy}
            )
            if not r.ok or not r.text:
                logger.debug("response not ok")
                p.remove_proxy(proxy)
                return

            test = BeautifulSoup(r.text, "html.parser")
            if test.title.text != "Google":
                logger.debug(f"title: \"{test.title.text}\" is not \"Google\"")
                p.remove_proxy(proxy)

        except Exception as e:
            logger.debug(e.__class__)
            p.remove_proxy(proxy)

    def worker():
        while True:
            item = q.get()
            logger.info(f"{q.qsize()} proxies to test.")
            if item is None:
                break
            test_proxy(item)
            q.task_done()

    q = Queue()
    threads = []
    for i in range(num_worker_threads):
        t = Thread(target=worker)
        t.start()
        threads.append(t)

    for item in p.proxies:
        q.put(item)

    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()
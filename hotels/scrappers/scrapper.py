import requests
from bs4 import BeautifulSoup

from hotels.proxy_pool import ProxyPool


class Scrapper:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def __init__(self, url, proxies=None):
        print("Scrapper initialised with url `{}`".format(url))
        self.url = url
        self.page = None
        self.soup = None
        self.proxies = proxies
        self.proxy_pool = None

    def _request(self):
        """
        Make the request on the URL.

        Later to include anti-blocking policies.
        Populates the page attribute.
        :return: None
        """
        if self.proxies is None:
            self.page = requests.get(self.url, headers=self.headers)
        else:
            self._request_with_proxies()

    def load_soup(self, use_proxy=True):
        if not use_proxy:
            self._request()
        else:
            self._request_with_proxies()
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    def get_html(self):
        return self.soup

    def _get_next_proxy(self):
        return next(self.proxy_pool)

    def _request_with_proxies(self):
        proxy_pool = ProxyPool.instance()
        while True:
            proxy = proxy_pool.get_proxy()
            print(f"using proxy {proxy}")

            try:
                self.page = requests.get(self.url, proxies={"http": proxy, "https": proxy}, headers=self.headers)
                print("Request is a success.")
                break

            except Exception as e:
                print("Connection Error for proxy {}".format(proxy))
                print(e)
                proxy_pool.remove_proxy(proxy)

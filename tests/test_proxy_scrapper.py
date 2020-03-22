import re
import unittest
from unittest import mock

from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper


class TestProxyScrapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_scrapper = ProxyScrapper("https://free-proxy-list.net/")
        cls.proxy_scrapper.get_proxies(False)

    def test_request(self):
        """
        Test that a simple request (without proxy) works.

        :param proxy_scrapper: ProxyScrapper
        :type proxy_scrapper: ProxyScrapper
        :return:
        """
        self.assertTrue(self.proxy_scrapper.list_proxies)  # not empty list is truthy

    def test_proxy_format(self):
        """
        Test that the proxy scrapped are correctly formatted.

        :param proxy_scrapper: ProxyScrapper
        :type proxy_scrapper: ProxyScrapper
        :return:
        """
        for prox in self.proxy_scrapper.list_proxies:
            proxy_re = re.compile(r'((\d{1,3})(\.|:)){4}\d+')
            self.assertTrue(proxy_re.search(prox).group() == prox)

    @mock.patch("hotels.scrappers.scrapper.requests.get")
    def test_request_with_proxy(self, mock_get):
        """
        :type mock_get: mock.MagickMock
        :type proxy_scrapper: ProxyScrapper
        :return:
        """
        ProxyPool().get_proxy = mock.Mock()
        ProxyPool().get_proxy.return_value = "proxy"

        url = "https://free-proxy-list.net/"
        test = ProxyScrapper(url)

        mock_get.return_value.text = "hello"

        a = test.get_proxies(True)
        mock_get.assert_called_with(
            headers=test.headers, proxies={'http': "proxy", 'https': "proxy"}, url=url, timeout=20,
        )

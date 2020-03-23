import re
import unittest
from unittest import mock

from hotels.scrappers.proxyscrapper import ProxyScrapper

list_proxies = ProxyScrapper("https://free-proxy-list.net/").get_proxies(False)


class TestProxyScrapper(unittest.TestCase):

    def test_request(self):
        """Test that getting proxy is still working."""
        self.assertTrue(len(list_proxies) > 0)  # not empty list is truthy

    def test_proxy_format(self):
        """Test that the proxy scrapped are correctly formatted."""
        for prox in list_proxies:
            proxy_re = re.compile(r'((\d{1,3})(\.|:)){4}\d+')
            self.assertTrue(proxy_re.search(prox).group() == prox)

    def test_request_with_proxy(self):
        """Test that a request with a proxy is working. (No error)"""
        url = "https://free-proxy-list.net/"
        test = ProxyScrapper(url)

        ProxyScrapper.simple_request = mock.Mock()
        ProxyScrapper.simple_request.return_value = "not none"

        test.page = mock.Mock()
        test.page.text = "hello"

        test.get_proxies(use_proxy=True)
        ProxyScrapper.simple_request.assert_called_with(use_proxy=True)

import re

import pytest

from hotels.scrappers.proxyscrapper import ProxyScrapper


@pytest.fixture(scope="module")
def proxy_scrapper():
    """

    :return: ProxyScrapper
    :rtype: ProxyScrapper
    """
    return ProxyScrapper("https://free-proxy-list.net/")


class TestProxyScrapper:
    def test_request(self, proxy_scrapper):
        """
        Test that a simple request (without proxy) works.

        :param proxy_scrapper: ProxyScrapper
        :type proxy_scrapper: ProxyScrapper
        :return:
        """
        proxy_scrapper.get_proxies()
        assert len(proxy_scrapper.list_proxies) != 0, "Proxy scrapper does not work."

    def test_proxy_format(self, proxy_scrapper):
        """
        Test that the proxy scrapped are correctly formatted.

        :param proxy_scrapper: ProxyScrapper
        :type proxy_scrapper: ProxyScrapper
        :return:
        """
        for prox in proxy_scrapper.list_proxies:
            test = re.compile(r'((\d{1,3})(\.|:)){4}\d+')
            assert test.search(prox).group() == prox

    # def test_request_with_proxy(self, proxy_scrapper):
    #     """
    #
    #     :type proxy_scrapper: ProxyScrapper
    #     :return:
    #     """
    #     ProxyPool(proxies=proxy_scrapper.list_proxies)
    #     test = ProxyScrapper("https://free-proxy-list.net/")
    #     a = test.get_proxies(True)
    #     print(a)

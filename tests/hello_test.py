from hotels.scrappers.proxyscrapper import ProxyScrapper


def test_something():
    assert True


class TestProxyScrapper:
    def test_request(self):
        ps = ProxyScrapper("https://free.currconv.com/api/v7/")
        proxies = ps.get_proxies(use_proxy=False)
        assert len(proxies) != 0, "Proxy scrapper does not work."

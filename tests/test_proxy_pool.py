import unittest

from hotels.proxy_pool import ProxyPool


def create_proxy_pool(proxies):
    pp = ProxyPool()
    pp.proxies = proxies
    pp.proxy_pool = pp._create_pool()
    return pp


class ProxyPoolTest(unittest.TestCase):
    def setUp(self) -> None:
        ProxyPool().proxies = None  # Reboots the proxy class.

    def test_cycle(self):
        """Test cycle behaviour."""
        pp = create_proxy_pool(['a', 'b'])
        self.assertEqual(pp.proxies, ["a", "b"])
        prox = []
        for _ in range(3):
            prox.append(pp.get_proxy())
        self.assertEqual(prox, ['a', 'b', 'a'])

    def test_remove(self):
        """Test that remove is working."""
        pp = create_proxy_pool(["a", "to_delete", "b"])
        pp.remove_proxy("to_delete")
        for _ in range(3):
            self.assertNotEqual(pp.get_proxy(), "to_delete")

    def test_stop_iter(self):
        """Test that an empty pool throws StopIteration error."""
        pp = create_proxy_pool([])  # simulates a pool being empty
        with self.assertRaises(StopIteration):
            pp.get_proxy()


if __name__ == '__main__':
    unittest.main()

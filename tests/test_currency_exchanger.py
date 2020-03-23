import unittest

from hotels import Conf
from hotels.currency_exchanger import CurrencyExchanger
from hotels.scrappers.scrapper import Scrapper
from hotels.utils.misc import init


class CurrencyExchangerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        init()

    def setUp(self) -> None:
        self.ce = CurrencyExchanger()

    def test_round_1(self):
        """Test that the rounding function behaves properly."""
        self.assertEqual(self.ce.round(1.2), 1)
        self.assertEqual(self.ce.round(1.8), 2)
        self.assertEqual(self.ce.round(5.0), 5)

    def test_call_api(self):
        """Test API is still up."""
        resp = Scrapper("https://free.currconv.com/others/usage?apiKey=2ab0a578e59c2ad88e54").simple_request()
        self.assertTrue(resp.ok)


if __name__ == '__main__':
    unittest.main()

import json
import unittest
from unittest import mock

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

    def test_no_redundant_call(self):
        """Test that the exchanger does not call API if not needed"""
        Scrapper.simple_request = mock.Mock()
        Scrapper.simple_request.return_value.text = json.dumps({"USD_EUR": 1.2})
        for _ in range(3):
            self.ce.convert_price(123, "US$", "EUR")

        Scrapper.simple_request.assert_called_once()  # instead of three.
        self.assertIsNotNone(self.ce.exchange_rates.get("USD_EUR"))

    def test_unknown_symb(self):
        self.assertIsNone(self.ce.convert_price(12, "unknown"))


if __name__ == '__main__':
    unittest.main()

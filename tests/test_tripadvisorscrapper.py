import unittest
from unittest import mock
from unittest.mock import call

from hotels.utils.conf import Conf

# verify that money changes.
NAME_TEST, SYMBOL_TEST = "ILS", "₪"
Conf().conf["TRIP_ADVISOR"]["currency_wanted_symbol"] = SYMBOL_TEST
Conf()["TRIP_ADVISOR"]["currency_wanted_name"] = NAME_TEST

from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper  # noqa

URL = "https://www.tripadvisor.co.uk/Hotels-g187162-Nancy_Meurthe_et_Moselle_Grand_Est-Hotels.html"


class TestTripAdvisorScrapper(unittest.TestCase):
    def setUp(self) -> None:

        self.scrapper = TripAdvisorScrapper

    @mock.patch("hotels.scrappers.tripadvisorscrapper.TripAdvisorScrapper.save_updates")
    def test_page(self, update_mock):
        """
        Test TripAdvisor on a first page, with a next page.

        Check that hotels, next_url, current page and page_max are all found
        Check that all detail url are found
        """

        hotels, next_url, elapsed_time, current_page, page_max = self.scrapper \
            .process_one_page(URL, headless=True, proxy=None, timeout=500, hotels=[])

        self.assertIsNotNone(next_url)
        self.assertIsNotNone(current_page)
        self.assertIsNotNone(page_max)
        self.assertTrue(len(hotels) > 0)

        for h in hotels:
            self.assertIsNotNone(h.detail_url)
            if h.price != "No price available":
                self.assertEqual(h.currency, NAME_TEST)
            else:
                self.assertEqual(h.currency, " ")

        update_mock.assert_called()  #
        return

    @mock.patch("hotels.scrappers.tripadvisorscrapper.TripAdvisorScrapper.process_one_page")
    def test_crawler(self, mock_process_one_page):
        mock_process_one_page.side_effect = [(["one hotel"], "something_else", 12.5, 1, 2),
                                             (["one hotel", "another one"], None, 12.5, 2, 2)]

        result = self.scrapper.crawler("something", use_proxy=False)

        self.assertEqual(
            mock_process_one_page.call_args_list,
            [call('something', True, [], proxy=None, timeout=300),
             call('something_else', True, ['one hotel'], proxy=None, timeout=300)]
        )

        self.assertEqual(result, ["one hotel", "another one"])

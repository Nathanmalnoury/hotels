import unittest
from unittest import mock

from click.testing import CliRunner

import hotels.click_commands as command
from hotels.models.hotel import Hotel


class TestClickCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @mock.patch("hotels.click_commands.TripAdvisorScrapper.crawler")
    @mock.patch("hotels.click_commands.save_as_excel")
    def test_scrap(self, mock_save_excel, crawler_mock):
        return_hotel = [Hotel(name="name", rating="4.5", votes=25, price=125, currency="£", commodities=[],
                              detail_url="/test.html")]

        crawler_mock.side_effect = [return_hotel]

        base_url = "https://www.tripadvisor.co.uk/Hotels-g298484-Moscow_Central_Russia-Hotels.html"
        excel_path = "/test.xlsx"
        show_browser = False
        timeout = 123
        no_proxy = True
        args = f"--base-url={base_url} --excel-path={excel_path} --timeout {timeout} --no-proxy"

        self.runner.invoke(cli=command.scrap, args=args)

        crawler_mock.assert_called_with(first_url=base_url, headless=not show_browser,
                                        use_proxy=not no_proxy, timeout=timeout)

        mock_save_excel.assert_called_with(return_hotel, excel_path)


if __name__ == '__main__':
    unittest.main()

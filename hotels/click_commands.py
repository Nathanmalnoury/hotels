import logging
import time

import click

from hotels.conf_reader import ConfReader
from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils.misc import init
from hotels.utils.hotels import save_as_excel
from hotels.utils.click_utils import check_args

conf = ConfReader.get("conf.ini")
logger = logging.getLogger("Hotels")


@click.group()
def scrapper():
    pass


@scrapper.command(help="Scrap a TripAdvisor page, get all pages available starting with the base-url.")
@click.option("--base-url", type=str, help="Url to start the scrapping with. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["base_url"])
@click.option("--excel-path", type=str, help="Path to save the excel sheet. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["excel_path"])
def scrap(base_url, excel_path):
    check_args(base_url, excel_path)
    init()
    logger.info(f"Scrapping starts. Path to save excel: '{excel_path}'")
    start = time.time()
    hotels = TripAdvisorScrapper.crawler(base_url=base_url)
    save_as_excel(hotels, excel_path)
    end = time.time()

    logger.info(f"Created Excel file, path: {excel_path}")
    logger.info(f"Processing took {end - start}")
    click.echo("Success.")
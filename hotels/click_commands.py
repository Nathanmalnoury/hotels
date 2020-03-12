import glob
import logging
import os
import time

import click

from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils.click_utils import check_args, check_excel
from hotels.utils.conf_reader import ConfReader
from hotels.utils.hotels import save_as_excel
from hotels.utils.misc import init

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


@scrapper.command(help="Recover data from a save and start scrapping based on the saved information.")
@click.option("--page", type=int, help="page number to get the save from.")
@click.option("--excel-path", type=str, help="Path to save the excel sheet. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["excel_path"])
def restart_from_save(page, excel_path):
    check_excel(excel_path)
    init()
    data = TripAdvisorScrapper.roll_back_from_save(page)
    logger.info(f"Recovered data from page {page}. Found {len(data['hotels'])} hotels.")
    start = time.time()
    url = "https://www.tripadvisor.co.uk" + data["next_link"]
    hotels = TripAdvisorScrapper.crawler(url, data=data)
    save_as_excel(hotels, excel_path)
    end = time.time()
    logger.info(f"Created Excel file, path: {excel_path}")
    logger.info(f"Processing took {end - start}")
    click.echo("Success.")


@scrapper.command(help="show saved files.")
def saves():
    path = conf["TRIP_ADVISOR"]["save_dir"]
    list_of_files = glob.glob(path + '*')  # * means all if need specific format then *.csv
    list_of_files.sort(key=os.path.getctime, reverse=True)
    for path in list_of_files:
        click.echo(os.path.basename(path))

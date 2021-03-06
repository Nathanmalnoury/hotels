"""CLI commands, using click."""
import glob
import logging
import os
import time

import click

from hotels.scrappers.tripadvisorscrapper import TripAdvisorScrapper
from hotels.utils.click_utils import check_args, check_excel
from hotels.utils.conf import Conf
from hotels.utils.hotels import save_as_excel
from hotels.utils.misc import init

conf = Conf()
logger = logging.getLogger("Hotels")


@click.group()
def scrapper():
    """Scrapper click group of commands."""
    pass


@scrapper.command(help="Scrap a TripAdvisor page, get all pages available starting with the base-url.")
@click.option("--base-url", type=str, help="Url to start the scrapping with. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["base_url"])
@click.option("--excel-path", type=str, help="Path to save the excel sheet. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["excel_path"])
@click.option("--timeout", type=int, help="Timeout for loading the TripAdvisor pages.",
              default=conf["TRIP_ADVISOR"]["timeout"])
@click.option("--show-browser", is_flag=True, help="Open the browser and show it to the user.", default=False)
@click.option("--no-proxy", is_flag=True, default=False, help="Requests made on TripAdvisor wont use a proxy")
def scrap(base_url, excel_path, timeout, show_browser, no_proxy):
    """Scrap a TripAdvisor page, get all pages available starting with the base-url."""
    logger.warning(base_url + excel_path + "{}".format(timeout))
    check_args(base_url, excel_path)
    init()
    logger.info(f"Scrapping starts. Path to save excel: '{excel_path}'")
    start = time.time()
    hotels = TripAdvisorScrapper.crawler(
        first_url=base_url,
        headless=not show_browser,
        use_proxy=not no_proxy,
        timeout=timeout
    )
    logger.warning(hotels)
    save_as_excel(hotels, excel_path)
    end = time.time()

    logger.info(f"Created Excel file, path: {excel_path}")
    logger.info(f"Processing took {end - start}")
    click.echo("Success.")


@scrapper.command(help="Recover data from a save and start scrapping based on the saved information.")
@click.option("--page", type=int, help="page number to get the save from.")
@click.option("--excel-path", type=str, help="Path to save the excel sheet. Use conf.ini by default",
              default=conf["TRIP_ADVISOR"]["excel_path"])
@click.option("--timeout", type=int, help="Timeout for loading the TripAdvisor pages.",
              default=conf["TRIP_ADVISOR"]["timeout"])
@click.option("--show-browser", is_flag=True, help="Open the browser and show it to the user.", default=False)
@click.option("--no-proxy", is_flag=True, default=False, help="Requests made on TripAdvisor wont use a proxy")
def restart_from_save(page, excel_path, timeout, show_browser, no_proxy):
    """Recover data from a save and start scrapping based on the saved information."""
    check_excel(excel_path)
    init()
    data = TripAdvisorScrapper.roll_back_from_save(page)
    logger.info(f"Recovered data from page {page}. Found {len(data['hotels'])} hotels.")
    start = time.time()
    url = "https://www.tripadvisor.co.uk" + data["next_link"]

    hotels = TripAdvisorScrapper.crawler(
        url,
        data=data,
        timeout=timeout,
        headless=not show_browser,
        use_proxy=not no_proxy
    )

    save_as_excel(hotels, excel_path)
    end = time.time()
    logger.info(f"Created Excel file, path: {excel_path}")
    logger.info(f"Processing took {end - start}")
    click.echo("Success.")


@scrapper.command(help="show saved files.")
def saves():
    """Show saved files."""
    path = conf.get_path("TRIP_ADVISOR", "save_dir")
    list_of_files = glob.glob(path + '*')  # * means all if need specific format then *.csv
    list_of_files.sort(key=os.path.getctime, reverse=True)
    for path in list_of_files:
        click.echo(os.path.basename(path))

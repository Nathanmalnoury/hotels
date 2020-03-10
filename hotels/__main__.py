#! /usr/bin/python3
import logging

import hotels.click_commands as click

logger = logging.getLogger("Hotels")

if __name__ == '__main__':
    click.scrapper()
    # hotels_found = get_hotels_save_as_excel(
    #     conf["TRIP_ADVISOR"]["base_url"],
    #     conf["TRIP_ADVISOR"]["excel_path"]
    # )

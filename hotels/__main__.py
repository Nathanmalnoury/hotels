#! /usr/bin/python3
import logging

import hotels.click_commands as click

logger = logging.getLogger("Hotels")

if __name__ == '__main__':
    click.scrapper()

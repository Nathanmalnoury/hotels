#! /usr/bin/python3
"""Main file, uses click to prompt cli commands."""
import logging

import hotels.click_commands as click

if __name__ == '__main__':
    logger = logging.getLogger("Hotels")
    click.scrapper()

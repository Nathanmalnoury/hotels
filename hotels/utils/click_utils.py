"""Util functions to check arguments format for click cli call."""
import logging
import os

logger = logging.getLogger("Hotels")


def check_args(url, excel_path):
    """Check that args are in appropriate format."""
    check_url(url)
    check_excel(excel_path)


def check_url(url):
    """
    Check url format.

    Check if url is a String, then that it correspond to the supported website (UK version of TripAdvisor)

    :param url: url to check
    :type url: Any
    :raise TypeError ValueError
    """
    if not type(url) == str:
        logger.error(f"Url should be a string, got a {type(url)}.")
        raise TypeError("Url is not a string.")
    should_start_with = "https://www.tripadvisor.co.uk/Hotels-"
    if not url.startswith(should_start_with):
        logger.error(f"Url should startwith '{should_start_with}', not '{url}'")
        raise ValueError("Url is not supported.")


def check_excel(excel_path):
    """
    Check path to Excel.

    Check that the path is a str, and that it corresponds to a real path in the system.
    Check that the format of the file to be written is also an xlsx.

    :param excel_path: path to check
    :type excel_path: any
    :return: None
    :raise TypeError OSError
    """
    if not type(excel_path) == str:
        logger.error(f"Path should be a string, got a {type(excel_path)}.")
        raise TypeError("Path is not a string.")
    if not os.path.exists(os.path.dirname(excel_path)):
        logger.error(f"Path does not point to a file. Path: '{excel_path}'")
        raise OSError("Path does not point to a file.")
    if not excel_path.endswith(".xlsx"):
        logger.error(f"Extension should be 'xlsx'. Current file name: '{os.path.basename(excel_path)}'")
        raise OSError("Wrong extension")

#!/usr/bin/env python3
"""Script responsible for handling the conf."""

import configparser
import os


class ConfReader:
    """Util class that reads the conf."""

    @staticmethod
    def get(filename):
        """
        Read conf file and store the default values in a dictionary.

        This only work if the conf file is in the root of the project folder !!
        :param filename: name of the conf fileDB
        :type filename: str
        :return: dict with the default values
        :rtype: dict
        """
        dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.dirname(os.path.dirname(dir_abs_path))
        path = os.path.join(root_path, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError("File not found. Are you sure of it's name ? Is it at the root of the folder ? ")
        config = configparser.ConfigParser()
        config.read(path)

        data = {}
        for section in config.sections():
            data[section] = dict(config.items(section))

        return data

#!/usr/bin/env python3
"""Script responsible for handling the conf."""

import configparser
import os

from hotels.utils.singleton import singleton


@singleton
class Conf(object):
    """Util class that reads the conf."""

    def __init__(self, file_name=None):
        if file_name is not None:
            self.conf = self._load(file_name)

    @staticmethod
    def _load(filename):
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

    def get(self, key, default=None):
        return self.conf.get(key, default)

    def __getitem__(self, item):
        return self.conf.get(item)

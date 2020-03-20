#!/usr/bin/env python3
"""Script responsible for handling the conf."""

import configparser
import os

from hotels.utils.singleton import singleton


@singleton
class Conf(object):
    """Util class that reads the conf."""

    def __init__(self, file_name=None):
        """Initialise Conf object."""
        if file_name is not None:
            self.conf = self._load(file_name)

    @staticmethod
    def _get_root_path():
        dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(dir_abs_path))

    @staticmethod
    def _load(filename):
        """
        Read conf file and store the default values in a dictionary.

        This only work if the conf file is in the root of the project folder !!
        :param filename: name of the conf fileDB
        :type filename: strConf
        :return: dict with the default values
        :rtype: dict
        """

        path = os.path.join(Conf()._get_root_path(), filename)

        if not os.path.isfile(path):
            raise FileNotFoundError("File not found. Are you sure of it's name ? Is it at the root of the folder ? ")
        config = configparser.ConfigParser()
        config.read(path)

        data = {}
        for section in config.sections():
            data[section] = dict(config.items(section))

        return data

    def get_path(self, section, key):
        return os.path.join(self._get_root_path(), self.conf[section][key])

    def get(self, key, default=None):
        """
        Implement a dict-like get.

        Get is done on self.conf, which is a dict(sections, {section data}).
        :param key: key to sea
        :type key: str
        :param default: to return if key is not found. default: None
        :return: section dict
        :rtype: dict
        """
        return self.conf.get(key, default)

    def __getitem__(self, item):
        """
        Implement getitem, to make Conf behave like a dict.

        Searches into self.conf, which is a dict(sections, {section data}).
        :param item: name of the item to find
        :type item: str
        :return result, as a dict
        :rtype: dict
        """
        return self.conf.get(item)

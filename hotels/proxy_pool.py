"""Singleton class to handle proxy."""
import logging
from itertools import cycle

from hotels.utils.singleton import singleton

logger = logging.getLogger("Hotels")


@singleton
class ProxyPool:
    """Proxy pool container."""

    def __init__(self, proxies=None):
        """
        Init for singleton proxypool.

        This will only be executed on the first instantiation, making the proxies useless for every next one.
        :param proxies:
        """
        if proxies is not None:
            self.proxies = proxies
            self.proxy_pool = self._create_pool()
            logger.debug(f'ProxyPool initialized with {len(self.proxies)} proxies')

    def _create_pool(self):
        return cycle(self.proxies)

    def get_proxy(self):
        """
        Get a proxy from proxy pool.

        :return: Proxy
        :rtype: str
        """
        return next(self.proxy_pool)

    def remove_proxy(self, proxy):
        """
        Remove a proxy from the proxy pool.

        :param proxy: proxy to remove,=.
        :type proxy: str
        :return: None
        """
        self.proxies.remove(proxy)
        self.proxy_pool = self._create_pool()
        logger.debug(f"ProxyPool updated. New number of proxies: {len(self.proxies)}")

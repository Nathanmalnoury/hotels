import logging
from itertools import cycle

from singleton.singleton import Singleton

logger = logging.getLogger("Hotels")


@Singleton
class ProxyPool:
    def __init__(self, proxies):
        self.proxies = proxies
        self.proxy_pool = self._create_pool()
        logger.debug(f'ProxyPool created with {len(self.proxies)} proxies')

    def _create_pool(self):
        return cycle(self.proxies)

    def get_proxy(self):
        return next(self.proxy_pool)

    def remove_proxy(self, proxy):
        self.proxies.remove(proxy)
        self.proxy_pool = self._create_pool()
        logger.debug(f"ProxyPool updated. New number of proxies: {len(self.proxies)}")

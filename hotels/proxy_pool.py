import logging
from itertools import cycle

from hotels.utils.singleton import singleton

logger = logging.getLogger("Hotels")


@singleton
class ProxyPool:
    def __init__(self, proxies=None):
        if proxies is not None:
            self.proxies = proxies
            self.proxy_pool = self._create_pool()
            self.proxy_pool = self._create_pool()
            logger.debug(f'ProxyPool initialized with {len(self.proxies)} proxies')

    def _create_pool(self):
        return cycle(self.proxies)

    def get_proxy(self):
        return next(self.proxy_pool)

    def remove_proxy(self, proxy):
        self.proxies.remove(proxy)
        self.proxy_pool = self._create_pool()
        logger.debug(f"ProxyPool updated. New number of proxies: {len(self.proxies)}")

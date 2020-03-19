import logging
import time

from selenium import webdriver

from hotels.proxy_pool import ProxyPool

logger = logging.getLogger("Hotels")


class WebDriver:
    @staticmethod
    def get(url, headless=True):

        while True:
            proxy_pool = ProxyPool()
            proxy = proxy_pool.get_proxy()
            driver = WebDriver._get_driver(proxy=proxy, headless=headless)

            try:
                driver.get(url)

                if not WebDriver._check_page(driver):
                    driver.quit()
                    proxy_pool.remove_proxy(proxy)
                    continue

                WebDriver._change_currency(driver)
                WebDriver._wait_prices(driver)

                if not WebDriver._check_page(driver):
                    driver.quit()
                    proxy_pool.remove_proxy(proxy)
                    continue

                logger.debug(f"Request is a success, for page '{driver.current_url}'")
                page = driver.page_source

                driver.quit()
                return page

            except Exception as e:
                driver.quit()
                proxy_pool.remove_proxy(proxy)
                logger.exception(e)

    @staticmethod
    def _get_driver(proxy, headless):
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server={proxy}')
        if headless:
            options.add_argument('--headless')

        driver = webdriver.Chrome(chrome_options=options)
        # chrome.set_page_load_timeout(200)  # Wait n sec before giving up on loading page
        driver.set_window_size(width=1700, height=500)  # makes sure the layout is the one supported by the parsers.
        return driver

    @staticmethod
    def _change_currency(driver):
        try:
            cur = driver.find_element_by_xpath("//span[@class='currency_symbol']")
            logger.debug(f"Currency before change '{cur.text}'.")
            if cur.text == "€":
                logger.info("No change in currency needed.")
                return True

            time.sleep(2)
            driver.find_element_by_xpath("//div[@data-header='Currency']").click()
            WebDriver._wait_currencies(driver)

            euro = driver.find_element_by_xpath("//div[@class='currency_code' and text() = 'EUR']/parent::node()")
            euro.click()

            # let time to request the new page, with new currency:
            time.sleep(2)

            logger.info("Change currency, success.")
            return True

        except Exception as e:
            logger.warning(f"Change currency, fail due to {e.__class__}.")
            return False

    @staticmethod
    def _wait_prices(driver):
        time.sleep(2)
        while True:
            elts_loader = driver.find_elements_by_xpath("//span[@class='ui_loader small']")
            elts_wrapper = driver.find_elements_by_xpath("//div[@class='relWrap']")
            if len(elts_loader) == 0 and len(elts_wrapper) != 0:
                logger.debug("Prices fully charged.")
                break
            elif len(elts_wrapper) == 0:
                logger.debug("currency window closing.")
                time.sleep(2)
            else:
                logger.debug("prices are charging.")
                time.sleep(2)

    @staticmethod
    def _wait_currencies(driver):
        while True:
            elts = driver.find_elements_by_xpath("//li[contains(@class, 'currency_item ui_link')]")
            if len(elts) == 0:
                logger.debug("currency changer window is not charged yet.")
                time.sleep(2)
            else:
                logger.debug("currency changer window charged.")
                break

    @staticmethod
    def _check_page(driver):
        """

        :param driver:
        :return: True if page is as expected, false otherwise
        :rtype: bool
        """
        if not driver.current_url.startswith("https://www.tripadvisor.co.uk/Hotels-"):
            logger.warning(f"Driver redirected ; '{driver.current_url}'.")
            logger.debug(driver.page_source)
            return False
        if WebDriver._page_is_error(driver):
            logger.warning("Driver landed on an error page.")
            return False
        if WebDriver._page_is_empty(driver):
            logger.warning("Driver landed on an empty page.")
            return False
        return True

    @staticmethod
    def _page_is_error(driver):
        err_detector = ["Privacy error", "error-information-button", "ERR_"]
        for err in err_detector:
            if err in driver.page_source:
                return True
        return False

    @staticmethod
    def _page_is_empty(driver):
        page = driver.page_source
        if page == "<html><head></head><body></body></html>":
            return True
        elif page is None:
            return True
        elif not page:
            return True
        else:
            return False

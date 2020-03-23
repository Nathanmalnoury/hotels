"""Driver for TripAdvisor Scrapping."""
import logging
import time

from selenium import webdriver

from hotels import Conf
from hotels.utils.misc import write_html_error

logger = logging.getLogger("Hotels")


class WebDriverTripAdvisor:
    """WebDriver based on selenium."""
    currency_wanted_symbol = Conf()["TRIP_ADVISOR"]["currency_wanted_symbol"]
    currency_wanted_name = Conf()["TRIP_ADVISOR"]["currency_wanted_name"]

    @staticmethod
    def get(url, proxy, timeout, headless=True):
        """
        Get a TripAdvisor UK url.

        Executes a change in currency where needed, and waits for prices to charge.
        Verifies that the returned page is adequate to what the scrappers are expecting.

        :param timeout: timeout
        :param proxy: Proxy to use. None -> does not use proxy
        :type proxy: None | str
        :param url: url
        :type url: str
        :param headless: whether to show the driver to the user or not.
        :type headless: bool
        :return: page
        """
        driver = WebDriverTripAdvisor._get_driver(proxy=proxy, headless=headless, timeout=timeout)

        try:
            s = time.time()
            driver.get(url)
            logger.debug(f"Get took {time.time() - s:.2f}s.")
            time.sleep(5)
            WebDriverTripAdvisor._handle_redirect(driver=driver)
            WebDriverTripAdvisor._check_page(driver)
            WebDriverTripAdvisor._change_currency(driver)

            try:
                WebDriverTripAdvisor._wait_prices(driver)
            except TimeoutError:
                logger.info("Prices did not charge in timeout limit.")
                driver.quit()

            WebDriverTripAdvisor._check_page(driver)
            logger.debug(f"Request is a success, for page '{driver.current_url}'. Took {time.time() - s:.2f}s.")
            page = driver.page_source

            driver.quit()
            return page

        except Exception as e:
            logger.exception(e)
            write_html_error(html_page=driver.page_source)
            driver.close()

    @staticmethod
    def _get_driver(proxy, headless, timeout):
        options = webdriver.ChromeOptions()
        if proxy is not None:
            options.add_argument(f'--proxy-server={proxy}')
            logger.debug(f"using proxy: '{proxy}'")
        if headless:
            options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)  # Wait 5 min before giving up on loading page
        driver.set_window_size(width=1700, height=500)  # makes sure the layout is the one supported by the parsers.
        return driver

    @staticmethod
    def _handle_redirect(driver):
        continue_element = driver.find_elements_by_xpath(
            "//span[contains(text(),'Continue your visit to www.tripadvisor.co.uk')]"
        )
        if len(continue_element) != 0:
            logger.info("detected a redirection.")
            continue_element[0].click()
            time.sleep(5)
        else:
            logger.debug("no redirection found.")

    @staticmethod
    def _change_currency(driver):
        try:
            cur = driver.find_element_by_xpath("//span[@class='currency_symbol']")
            logger.debug(f"Currency before change '{cur.text}'.")
            if cur.text == WebDriverTripAdvisor.currency_wanted_symbol:
                logger.info("No change in currency needed.")
                return True

            time.sleep(2)
            driver.find_element_by_xpath("//div[@data-header='Currency']").click()
            WebDriverTripAdvisor._wait_currencies(driver)

            euro = driver.find_element_by_xpath(
                f"//div[@class='currency_code' and text() = '{WebDriverTripAdvisor.currency_wanted_name}']"
                f"/parent::node()")
            euro.click()

            # let time to request the new page, with new currency:
            time.sleep(5)
            logger.info("Change currency, success.")
            return True

        except Exception as e:
            logger.warning(f"Change currency, fail due to {e.__class__}.")
            write_html_error(driver.page_source)
            return False

    @staticmethod
    def _wait_prices(driver):
        counter = 0
        time.sleep(2)
        while True:
            counter += 1
            elts_loader = driver.find_elements_by_xpath("//span[@class='ui_loader small']")
            elts_wrapper = driver.find_elements_by_xpath("//div[@class='relWrap']")
            elts_footer = driver.find_elements_by_xpath(
                "//div[@class='unified ui_pagination standard_pagination ui_section listFooter']"
            )

            if counter > 60:  # 120 sec
                raise TimeoutError("prices loading timeout.")

            if len(elts_loader) == 0 and len(elts_wrapper) != 0 and len(elts_footer) != 0:
                logger.debug("Prices fully charged.")
                break

            elif len(elts_wrapper) == 0:
                logger.debug("currency window closing, or page not loaded.")
            elif len(elts_footer) == 0:
                logger.debug("page is loading.")
            else:
                logger.debug("prices are charging.")
            time.sleep(2)

    @staticmethod
    def _wait_currencies(driver):
        loop_counter = 0
        while True:
            elts = driver.find_elements_by_xpath("//li[contains(@class, 'currency_item ui_link')]")
            loop_counter += 1
            if loop_counter > 45:  # 90sec
                raise TimeoutError("currency changer window timeout")
            if len(elts) == 0:
                logger.debug("currency changer window is not charged yet.")
                time.sleep(2)
            else:
                logger.debug("currency changer window charged.")
                break

    @staticmethod
    def _check_page(driver):
        """
        Run check on page.

        Runs redirect detection, _page_is_error and _page_is_empty.

        :param driver: driver
        :type driver: webdriver.Chrome
        :return: True if page is as expected, false otherwise
        :rtype: bool
        """
        if not driver.current_url.startswith("https://www.tripadvisor.co.uk/Hotels-"):
            write_html_error(driver.page_source)
            driver.quit()
            raise RedirectedError(f"redirected to {driver.current_url}")
        if WebDriverTripAdvisor._page_is_error(driver):
            driver.quit()
            logger.warning("Driver landed on an error page.")
            raise LandedOnErrorPageError
        if WebDriverTripAdvisor._page_is_empty(driver):
            driver.quit()
            logger.warning("Driver landed on an empty page.")
            raise EmptyPageError

    @staticmethod
    def _page_is_error(driver):
        """Check if page is an error page."""
        err_detector = ["Privacy error", "error-information-button", "ERR_"]
        for err in err_detector:
            if err in driver.page_source:
                return True
        return False

    @staticmethod
    def _page_is_empty(driver):
        """Check if page is empty."""
        page = driver.page_source
        if page == "<html><head></head><body></body></html>":
            return True
        elif page is None:
            return True
        elif not page:
            return True
        else:
            return False


class EmptyPageError(Exception):
    """Error to throw when the driver gets a empty page."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message is not None:
            return f"EmptyPageError, {self.message}"
        else:
            return "EmptyPageError has been raised"


class RedirectedError(Exception):
    """Error to throw the driver gets redirected."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message is not None:
            return f"RedirectedError, {self.message}"
        else:
            return "RedirectedError has been raised"


class LandedOnErrorPageError(Exception):
    """Error to throw when driver lands on an error page."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message is not None:
            return f"LandedOnErrorPageError, {self.message}"
        else:
            return "LandedOnErrorPageError has been raised"

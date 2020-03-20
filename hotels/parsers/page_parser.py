"""Parser for page information."""
import logging
import re

logger = logging.getLogger("Hotels")


class PageParser:
    """Parser to get information about the current page, the total page number and the next page url."""

    def __init__(self, str_page):
        """
        Init.

        :param str_page: Formatted HTML.
        """
        self.str_page = str_page

    def get_info(self):
        """Parse all util informatiom from given HTML."""
        page_number = self.get_page_number()
        next_link = self.get_next_page_link()
        current_page = self.get_current_page_number()
        info = {'total_page': page_number, 'next_link': next_link, 'current_page': current_page}
        logger.debug(info)
        return info

    def get_page_number(self):
        """Get the total number of pages from HTML."""
        matcher = re.compile(r'data-numpages="\d+"')
        info = matcher.search(self.str_page).group()
        info = info.split("\"")
        return int(info[1])

    def get_next_page_link(self):
        """Get the url to the next page from HTML."""
        try:
            matcher = re.compile(r'<.*class="nav next ui_button primary[\w\W]+?</')
            all = matcher.findall(self.str_page)
            logger.info(all)
            tag = matcher.search(self.str_page).group()
            href_matcher = re.compile(r"'/.*?\.html'")
            href = href_matcher.search(tag).group()
            logger.info(href)
            href = href.split("\'")
            logger.debug(href)
            return href[1]
        except:
            return None

    def get_current_page_number(self):
        """Get the current page number from HTML."""
        matcher = re.compile(r'<.* current [\w\W]+?</')
        tag = matcher.search(self.str_page).group()
        number = tag.split("\n")[1]
        return int(number.strip())

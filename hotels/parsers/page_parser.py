import logging
import re

logger = logging.getLogger("Hotels")

class PageParser:
    def __init__(self, str_page):
        self.str_page = str_page

    def get_info(self):
        page_number = self.get_page_number()
        next_link = self.get_next_page_link()
        current_page = self.get_current_page_number()
        info = {'total_page': page_number, 'next_link': next_link, 'current_page': current_page}
        logger.debug(info)
        return info

    def get_page_number(self):
        matcher = re.compile(r'data-numpages="\d+"')
        info = matcher.search(self.str_page).group()
        info = info.split("\"")
        return int(info[1])

    def get_next_page_link(self):
        try:
            matcher = re.compile(r'<.*class="nav next ui_button primary[\w\W]+?</')
            tag = matcher.search(self.str_page).group()
            href_matcher = re.compile(r"'/.*?\.html'")
            href = href_matcher.search(tag).group()
            href = href.split("\'")
            logger.debug(href)
            return href[1]
        except:
            return None

    def get_current_page_number(self):
        matcher = re.compile(r'<.* current [\w\W]+?</')
        tag = matcher.search(self.str_page).group()
        number = tag.split("\n")[1]
        return int(number.strip())

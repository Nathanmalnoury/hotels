import re


class PageParser:
    def __init__(self, str_page):
        self.str_page = str_page

    def get_info(self):
        page_number = self.get_page_number()
        next_link = self.get_next_page_link()
        current_page = self.get_current_page_number()
        return {'total_page': page_number, 'next_link': next_link, 'current_page': current_page}

    def get_page_number(self):
        matcher = re.compile(r'data-numpages="\d+"')
        info = matcher.search(self.str_page).group()
        info = info.split("\"")
        return int(info[1])

    def get_next_page_link(self):
        try:
            matcher = re.compile(r'<a class="nav next ui_button primary[\w\W]+?</a>')
            tag = matcher.search(self.str_page).group()
            href_matcher = re.compile(r'href=".*?"')
            href = href_matcher.search(tag).group()
            href = href.split("\"")
            return href[1]
        except:
            return None

    def get_current_page_number(self):
        matcher = re.compile(r'.* current [\w\W]+?</a>')
        tag = matcher.search(self.str_page).group()
        number = tag.split("\n")[1]
        return int(number.strip())

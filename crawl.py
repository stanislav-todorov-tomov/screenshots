import os
import string
import uuid
import random
from typing import List, Optional
from urllib.parse import urlparse, urldefrag, urljoin

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Locator, ElementHandle, Page

from config import Configuration
from data_access import DataAccess


class Crawler:

    def __init__(self):
        self._base_dir = Configuration().base_dir()
        self._data_access = DataAccess()

    def crawl(self, start_url: str, max_links: int) -> str:
        with sync_playwright() as playwright:
            firefox: Browser = playwright.firefox.launch()
            context: BrowserContext = firefox.new_context()
            page: Page = context.new_page()

            base_element: Optional[ElementHandle] = page.query_selector('base')
            if base_element and base_element.get_attribute('href'):
                base_url: str = base_element.get_attribute('href')
            else:
                base_url: str = start_url

            page.goto(start_url)
            a_elements: Locator = page.locator('a:visible')
            links: List[str] = [start_url]
            for a in a_elements.all():
                href_attr: str = a.get_attribute("href")
                if not href_attr or href_attr.endswith('.css') or href_attr.endswith('.svg') or href_attr.endswith(
                        '.xml'):
                    continue
                parsed_url = urlparse(href_attr)
                if parsed_url.scheme and parsed_url.netloc:
                    links.append(urldefrag(href_attr).url)
                else:
                    links.append(urldefrag(urljoin(base_url, href_attr)).url)

            dir_name = str(uuid.uuid4())
            links = links[:max_links] if len(links) > max_links else links
            for link in links:
                page.goto(link)
                file_name: str = ''.join(random.choices(population=string.ascii_lowercase, k=8)) + '.png'
                page.screenshot(path=os.path.join(self._base_dir, dir_name, file_name), full_page=True)

            firefox.close()
            return self._data_access.add_run(run_name=dir_name)

#! /usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time

from conf import urls

SLEEP_SECONDS = 5

class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(30)

    def crawl(self):
        time.sleep(SLEEP_SECONDS)

        # Test with one for now
        self.driver.get(urls[0])

        time.sleep(SLEEP_SECONDS)

        # Find ads
        els = self.driver.find_elements_by_class_name('ad')

        for el in els:
            print el.get_attribute('innerHTML')

        # TODO: Get image
        # http://stackoverflow.com/questions/15018372/how-to-take-partial-screenshot-with-selenium-webdriver-in-python

if __name__ == '__main__':
    c = Crawler()
    c.crawl()

#! /usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from PIL import Image

import logging
import time
import uuid
import io
import os
import base64
import json

from conf import urls

import pdb

PAGE_LOAD_TIMEOUT_SECONDS = 30
SLEEP_SECONDS = 15
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

OUT_DIR = 'out'

logging.basicConfig(level=logging.DEBUG)

class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)
        self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)

    def crawl(self):
        ads = []

        # Test with one for now
        self.driver.get(urls[0])

        time.sleep(SLEEP_SECONDS)

        # Find ads
        els = self.driver.find_elements_by_class_name('ad')

        main_window = self.driver.current_window_handle

        for idx, el in enumerate(els):
            logging.info('Processing element: {0}'.format(idx))

            img_id = str(uuid.uuid4())

            filename = 'screenshot-' + img_id + '.jpg'
            filepath = os.path.join(OUT_DIR, filename)

            # From http://stackoverflow.com/questions/15018372/how-to-take-partial-screenshot-with-selenium-webdriver-in-python
            # and http://stackoverflow.com/questions/37882208/get-element-location-relative-to-viewport-with-selenium-python
            self.driver.execute_script("return arguments[0].scrollIntoView();", el)
            self.driver.execute_script("window.scrollBy(0, -150);")
            self.driver.save_screenshot(filepath)

            scroll = self.driver.execute_script("return window.scrollY;")
            location = el.location
            size = el.size

            if size['height'] == 0 or size['width'] == 0:
                continue

            # Switch to main window
            self.driver.switch_to_window(main_window)

            # From http://stackoverflow.com/questions/27775759/send-keys-control-click-selenium
            # Cmd + Click to get to the new tab
            ActionChains(self.driver) \
                .key_down(Keys.COMMAND) \
                .click(el) \
                .key_up(Keys.COMMAND) \
                .perform()

            curr_url = None
            if len(self.driver.window_handles) > 1:
                # Switch to new tab, get url, and close it so we go back to the main window
                self.driver.switch_to_window(self.driver.window_handles[1])

                time.sleep(2)

                curr_url = self.driver.current_url
                logging.info('Current URL {0}'.format(curr_url))

                self.driver.close()
            else:
                logging.error('Unable to switch to new tab')

            self.driver.switch_to_window(main_window)

            im = Image.open(filepath)

            left = location['x']
            top = location['y'] - scroll
            right = location['x'] + size['width']
            bottom = location['y'] + size['height'] - scroll

            logging.debug('Scroll: {}'.format(scroll))
            logging.debug('Size: {}'.format(size))
            logging.debug('Location: {}'.format(location))

            filepath_ad = filepath.replace('.jpg', '-ad.jpg')

            im = im.crop((left, top, right, bottom))
            im.save(filepath_ad)

            ads.append({
                'img_id': img_id,
                'orig': filepath,
                'ad': filepath_ad,
                'curr_url': curr_url,
                })

        self.driver.quit()

        return ads

if __name__ == '__main__':
    c = Crawler()
    ads = c.crawl()

    # Don't need this now since we're just using the landing page URLs
    # ads = c.detect_text(ads)

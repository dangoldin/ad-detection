#! /usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from PIL import Image

import requests
import logging
import time
import uuid
import io
import os
import base64
import json
import re

from conf import urls

import pdb

PAGE_LOAD_TIMEOUT_SECONDS = 30
SLEEP_SECONDS = 15
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

RE_TWITTER = re.compile('twitter\.com\/(.+?)"')

OUT_DIR = 'out'

logging.basicConfig(level=logging.DEBUG)

class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)
        self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)

    def find_twitter_account(self, url):
        if url is not None:
            try:
                r = requests.get(url)
                twitter_accounts = RE_TWITTER.findall(r.content)
                if len(twitter_accounts) > 0:
                    return twitter_accounts[0]
            except Exception as e:
                logging.exception('Failed to fetch {0}'.format(url))
        return None

    def crawl(self):
        ads = []

        # Test with one for now
        self.driver.get(urls[0])

        time.sleep(SLEEP_SECONDS)

        # Find ads
        els = self.driver.find_elements_by_class_name('ad')

        main_window = self.driver.current_window_handle

        run_id = str(uuid.uuid4())

        os.mkdir(os.path.join(OUT_DIR, run_id))

        for idx, el in enumerate(els):
            logging.info('Processing element: {0}'.format(idx))

            img_id = str(idx)

            filename = 'screenshot-' + img_id + '.jpg'
            filepath = os.path.join(OUT_DIR, run_id, filename)

            # From http://stackoverflow.com/questions/15018372/how-to-take-partial-screenshot-with-selenium-webdriver-in-python
            # and http://stackoverflow.com/questions/37882208/get-element-location-relative-to-viewport-with-selenium-python
            self.driver.execute_script("return arguments[0].scrollIntoView();", el)
            self.driver.execute_script("window.scrollBy(0, -150);")
            self.driver.save_screenshot(filepath)

            scroll = self.driver.execute_script("return window.scrollY;")
            location = el.location
            size = el.size

            # No valid ad found so clean up
            if size['height'] == 0 or size['width'] == 0:
                os.remove(filepath)
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
                'twitter_account': self.find_twitter_account(curr_url),
                })

        self.driver.quit()

        with open(os.path.join(OUT_DIR, run_id, 'out.json'), 'w') as f:
            f.write(json.dumps(ads, indent=2))

        return ads

if __name__ == '__main__':
    c = Crawler()
    ads = c.crawl()

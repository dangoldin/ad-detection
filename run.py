#! /usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from googleapiclient import discovery
from googleapiclient import errors

from oauth2client.client import GoogleCredentials

from PIL import Image

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

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

OUT_DIR = 'out'

class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_SECONDS)
        self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def crawl(self):
        ads = []

        # Test with one for now
        self.driver.get(urls[0])

        time.sleep(SLEEP_SECONDS)

        # Find ads
        els = self.driver.find_elements_by_class_name('ad')

        main_window = self.driver.current_window_handle

        for idx, el in enumerate(els):
            print 'Processing element', idx

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
                print 'Current URL', curr_url

                self.driver.close()
            else:
                print 'Unable to switch to new tab'

            self.driver.switch_to_window(main_window)

            im = Image.open(filepath)

            left = location['x']
            top = location['y'] - scroll
            right = location['x'] + size['width']
            bottom = location['y'] + size['height'] - scroll

            print 'Scroll', scroll
            print 'Size', size
            print 'Location', location

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

    # # From https://github.com/GoogleCloudPlatform/cloud-vision/blob/master/python/text/textindex.py
    # def detect_text(self, ads, num_retries=3, max_results=6):
    #     input_filenames = [os.path.join(OUT_DIR, 'screenshot-' + ad['img_id'] + '-2.jpg') for ad in ads]

    #     images = {}
    #     for filename in input_filenames:
    #         with open(filename, 'rb') as image_file:
    #             images[filename] = image_file.read()

    #     batch_request = []
    #     for filename in images:
    #         batch_request.append({
    #             'image': {
    #                 'content': base64.b64encode(
    #                         images[filename]).decode('UTF-8')
    #             },
    #             'features': [{
    #                 'type': 'TEXT_DETECTION',
    #                 'maxResults': max_results,
    #             }]
    #         })
    #     request = self.service.images().annotate(
    #         body={'requests': batch_request})

    #     try:
    #         responses = request.execute(num_retries=num_retries)
    #         if 'responses' not in responses:
    #             return {}
    #         text_response = {}
    #         for filename, response in zip(images, responses['responses']):
    #             if 'error' in response:
    #                 print("API Error for %s: %s" % (
    #                         filename,
    #                         response['error']['message']
    #                         if 'message' in response['error']
    #                         else ''))
    #                 continue
    #             if 'textAnnotations' in response:
    #                 textAnnotations = response['textAnnotations']
    #             else:
    #                 textAnnotations = []
    #             text_response[filename] = textAnnotations
    #             with open(filename + '.txt', 'w') as f:
    #                 f.write(json.dumps(textAnnotations, indent=2))
    #         return text_response
    #     except errors.HttpError as e:
    #         print("Http Error for %s: %s" % (filename, e))
    #     except KeyError as e2:
    #         print("Key error: %s" % e2)

    #     return ads

    # def identify_company(self, input_filenames):
    #     annotation_info = {}
    #     for filename in input_filenames:
    #         with open(filename, 'r') as f:
    #             annotation_info[filename] = json.loads(f.read())

    #     for filename in input_filenames:
    #         text = annotation_info[filename][0]['description']

    #         # TODO: actually figure out how to go from text to company name


if __name__ == '__main__':
    c = Crawler()
    ads = c.crawl()

    # Don't need this now since we're just using the landing page URLs
    # ads = c.detect_text(ads)

#! /usr/bin/env python

"""Super simple utility to save data to a Google spreadsheet"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Saver(object):
    def __init__(self, cred_file='client_secret.json'):
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
        self.client = gspread.authorize(creds)

    def open_workbook(self, workbook_name):
        self.sheet = self.client.open(workbook_name).sheet1

    def get_rows(self):
        return self.sheet.get_all_records()

    def num_rows(self):
        return len(self.sheet.get_all_records())

    def insert_row(self, vals):
        self.sheet.insert_row(vals, self.num_rows() + 2)

if __name__ == '__main__':
    SAVER = Saver(cred_file='client_secret.json')
    SAVER.open_workbook('Sleeping Giants Data')
    print SAVER.num_rows()
    SAVER.insert_row(['C', 'B', 'A'])

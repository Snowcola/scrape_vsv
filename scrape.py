import re
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_entry_list(base_url):
    entries = []
    r = requests.get(site_url + '?typ=list')
    soup = BeautifulSoup(r.content, 'html.parser')

    pattern = re.compile(r"id=([\d]+)")

    table = soup.find('table', 'mitgliederliste')
    links = table.find_all('a', href=True)

    for link in links:
        link_text = link['href']
        try:
            re_match = re.search(pattern, link_text)
            id = re_match.group(1)
            entries.append(id)
        except AttributeError:
            print(f'No id in link {link_text}')

    return set(entries)


def gather_entry_data(base_url, ids):
    entry_data = []
    for id in ids:
        data = dict()
        r = requests.get(base_url + '?typ=detail&id=' + id)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', 'mitgliedersuche')
        rows = table.find_all('tr')
        for row in rows:
            category = row.find('td').text
            contents = row.find('td', 'border').text
            if category == '\xa0':
                continue
            data[category] = contents
        print(data)
        entry_data.append(data)
    return entry_data


def scrape(base_url):
    entries = ['1157']  # get_entry_list(base_url)
    data = gather_entry_data(base_url, entries)

    return data


if __name__ == '__main__':
    base_url = 'https://www.vsv-asg.ch/en/mitgliedersuche'
    data = scrape(base_url)
    # data.to_excel(f'scraping_results_{datetime.now()}')

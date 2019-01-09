import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# initialize selenium (for js protected fields)
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument("--headless")
options.add_argument('--log-level=3')
options.binary_location = ""
driver = webdriver.Chrome(chrome_options=options)


def get_entry_list(base_url):
    entries = []
    r = requests.get(base_url + '?typ=list')
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

    return list(set(entries))


def gather_entry_data(base_url, ids):
    entry_data = []
    for i, item in enumerate(ids):
        print(f' Progress: ({i}/{len(ids)})', end='\r', flush=True)
        url = base_url + '?typ=detail&id=' + item
        data = dict()

        driver.get(url)
        source = driver.page_source

        soup = BeautifulSoup(source, 'html.parser')
        table = soup.find('table', 'mitgliedersuche')
        rows = table.find_all('tr')

        for row in rows:
            category = row.find('td').text
            contents = row.find('td', 'border').text

            if category == '\xa0':
                continue

            if category == 'E-Mail':
                email_pattern = re.compile(
                    r"[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*")
                email = re.search(email_pattern, contents)
                try:
                    contents = email.group(0)
                except IndexError:
                    pass

            data[category] = contents
        entry_data.append(data)
    return entry_data


def scrape(base_url):
    entries = get_entry_list(base_url)
    data = gather_entry_data(base_url, entries)
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    base_url = 'https://www.vsv-asg.ch/en/mitgliedersuche'
    data = scrape(base_url)
    time = datetime.now().strftime('%d%m%Y%I%M%S')
    data.to_excel(f'scraping_results_{time}.xlsx')
    driver.quit()

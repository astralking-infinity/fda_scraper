#!/usr/bin/python3

import json
import requests
import time
from collections import OrderedDict
from lxml import html
from urllib.parse import urljoin


def link_finder():
    '''
    Create a function to find all links of the products
    '''

    categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                  'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                  'Y', 'Z', '0-9']
    base_url = 'https://www.accessdata.fda.gov'
    d = OrderedDict()

    for category in categories:
        url = 'https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=browseByLetter.page&productLetter={}'.format(category)
        print('Processing...', url)
        while True:
            try:
                resp = requests.get(url)

                start_time = time.time()

                tree = html.fromstring(resp.text)

                XPATH_PRODUCT_LINKS = '//ul[contains(@id, "drugName")]//a/@href'

                raw_links = tree.xpath(XPATH_PRODUCT_LINKS)

                print('Number of links in {} Category:'.format(category), str(len(raw_links)))
                links = []
                for link in raw_links:
                    links.append(urljoin(base_url, link))

                d[category] = links
                break
            except Exception as e:
                print(e)

        delay = time.time() - start_time
        if delay <= 30:
            time.sleep(30 - delay)

    f = open('FDA_products.json', 'w')
    json.dump(d, f, indent=4)
    f.close()


def product_scraper(urls):
    '''
    Create a function to extract data within a link
    '''

    d = OrderedDict()
    products = []
    for url in urls:
        print('Processing...', url)
        while True:
            try:
                resp = requests.get(url)

                tree = html.fromstring(resp.text)

                XPATH_ROWS = '//table[@id="exampleProd"]//tbody//tr'
                raw_products_rows = tree.xpath(XPATH_ROWS)

                if not isinstance(raw_products_rows, list):
                    raw_products_rows = [raw_products_rows]

                for product_row in raw_products_rows:
                    XPATH_COLS = './/td/text()'
                    details = product_row.xpath(XPATH_COLS)

                    drug_name = details[0]
                    active_ingredients = details[1]
                    strength = details[2]
                    dosage_form = details[3]
                    marketing_status = details[4]
                    rld = details[5]
                    te_code = details[6].strip()

                    d.update({'drug name': drug_name,
                              'active ingredients': active_ingredients,
                              'strength': strength,
                              'dosage form/route': dosage_form,
                              'marketing status': marketing_status,
                              'rld': rld,
                              'te code': te_code})
                    products.append(d)
                    break
            except Exception as e:
                print(e)

        time.sleep(3)

    f = open('FDA_product_details.json', 'w')
    json.dump(d, f, indent=4)
    f.close()


if __name__ == '__main__':
    # link_finder()
    f = open('FDA_products.json')
    json_f = json.load(f)
    product_scraper([json_f['J'][0]])

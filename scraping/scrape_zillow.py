import random
import time
import pandas as pd
import re

import requests
from bs4 import BeautifulSoup
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


ZILLOW_BASE_URL = "https://www.zillow.com"

ZILLOW_FILE_PATH = "data/zillow_data.csv"


def get_address_from_xml(xml):
    pattern = re.compile(r"homedetails/(.*?)/\d+_zpid")
    address = re.search(pattern, xml).group(1)
    address = address.replace("-", " ")
    address = re.sub(r"\b(San Diego)", r", \1", address)
    address = re.sub(r"\b(CA)", r", \1", address)
    address = re.sub(r'\s+,', ',', address)

    return address


def get_zillow_listings(city="San-Diego"):
    """
    Scrapes Zillow for rental listings in a given city/state.
    Returns a list of dictionaries with listing details.
    """
    url = "https://www.zillow.com/xml/indexes/us/hdp/for-rent.xml.gz"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Zillow data: {e}")
        return []

    soup = BeautifulSoup(response.text, 'xml')
    xml = [loc.get_text() for loc in soup.find_all('loc')][0]

    response2 = requests.get(xml, timeout=10)
    soup2 = BeautifulSoup(response2.text, 'xml')
    xml2 = [loc.get_text() for loc in soup2.find_all('loc')]

    filtered_urls = [url for url in xml2 if city in url]
    logger.info(f"Scrapping data from {len(filtered_urls)} listings in San-Diego")

    user_agents = [
        "Chrome/112.0.0.0 Safari/537.36",
        "Chrome/114.0.0.0 Safari/537.36",
        "Chrome/115.0.5790.102 Safari/537.36",
        "Chrome/113.0.5672.63 Safari/537.36",
        "Chrome/112.0.5615.49 Safari/537.36",
        "Chrome/118.0.5993.91 Safari/537.36",
    ]

    listings = []
    for xml in filtered_urls:
        address_from_xml = get_address_from_xml(xml)
        selected_user_agent = random.choice(user_agents)
        chrome_options = Options()
        chrome_options.add_argument(f"user-agent={selected_user_agent}")
        chrome_options.add_argument("--headless")  # run headless
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(xml)
        html = driver.page_source

        listing_soup = BeautifulSoup(html, 'html.parser')

        try:
            title = ''
            if listing_soup.find('title'):
                title = listing_soup.find('title').text
            if title and title == "Access to this page has been denied":
                time.sleep(300)
                continue
            price_div = listing_soup.find_all('div', class_='hdp__sc-1r7qxf2-1 ghbhhz')
            if not price_div:
                price_div = listing_soup.find_all('div', class_='styles__StyledPriceAndBathWrapper-fshdp-8-106-0__sc-ncazb7-1 gLMzeO')
            price_span = price_div[0].find('span').text
            price = price_span
            address = listing_soup.find('div', class_='styles__AddressWrapper-fshdp-8-106-0__sc-13x5vko-0 dnABLg').find('h1').text
            cleaned_address = address.replace('\xa0', ' ')
            listing = {'price': price, 'address': cleaned_address, 'address_from_xml': address_from_xml}
            listings.append(listing)
            logger.info(f"Listing: {listing}")
            try:
                df = pd.read_csv(ZILLOW_FILE_PATH, index_col=False)
                new_row = pd.DataFrame({key: [value] for key, value in listing.items()})
                df = pd.concat([df, new_row], ignore_index=True)
                df.drop(columns=["Unnamed: 0"], inplace=True)
                df.to_csv(ZILLOW_FILE_PATH)
            except FileNotFoundError:
                df = pd.DataFrame(listings)
                df.to_csv(ZILLOW_FILE_PATH)
            time.sleep(3)
        except Exception as e:
            logger.error(str(e))
        finally:
            driver.quit()

    return listings

get_zillow_listings("San-Diego")
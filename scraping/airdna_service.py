# css-f95df6
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


chrome_options = Options()
chrome_options.add_argument("--headless")  # run headless

driver = webdriver.Chrome(options=chrome_options)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def clean_airdna_price(price_str):
    """
    Convert price strings like '$79.3K' into raw numbers (e.g., 79300).

    :param price_str: str, raw price string from AirDNA (e.g., "$79.3K", "$100K")
    :return: int, cleaned numerical value (e.g., 79300, 100000)
    """
    if not price_str:
        return None  # Handle empty or invalid values

    # Remove '$' and convert 'K' to thousand
    price_str = price_str.replace("$", "").strip()

    if 'K' in price_str:
        price_str = price_str.replace("K", "")
        try:
            return int(int(float(price_str) * 1000)/12)  # Convert to integer
        except ValueError:
            return None  # Handle unexpected format

    try:
        return int(price_str)/12  # Direct conversion for numbers without 'K'
    except ValueError:
        return None  # Handle unexpected format


def login_airdna():
    url = "https://app.airdna.co/data/login"

    # opening link in the browser
    driver.get(url)
    time.sleep(5)

    email = driver.find_element(By.NAME, 'email')
    email.send_keys("nilay.fullstack@gmail.com")

    password = driver.find_element(By.NAME, 'password')
    password.send_keys("Nilay@123")

    submit_button = driver.find_element(By.CLASS_NAME, 'MuiButtonBase-root')
    submit_button.click()

    return driver


def get_projected_revenue(address_list):
    driver = login_airdna()
    time.sleep(5)
    result = {}

    try:
        for address in address_list:
            try:
                # driver.set_page_load_timeout(10)  # Set timeout for page load
                driver.get('https://app.airdna.co/data/us?lat=40.43509&lng=-96&zoom=4.25')
            except TimeoutException:
                print(f"Timeout loading AirDNA for address: {address}")
                result[address] = "Error: Page Load Timeout"
                continue

            time.sleep(3)

            # Try to find the input box
            try:
                print(f"Finding projected revenue for: {address}")
                input_box = driver.find_element(By.CLASS_NAME, 'css-f95df6')
            except NoSuchElementException:
                print(f"Input box not found for address: {address}")
                result[address] = None
                continue

            # Send address and search
            input_box.send_keys(address)
            time.sleep(2)
            input_box.send_keys(Keys.RETURN)
            time.sleep(5)

            # Try to get revenue
            try:
                revenue_element = driver.find_element(By.CLASS_NAME, 'css-6xs9nt')
                result[address] = int(clean_airdna_price(revenue_element.text))
            except NoSuchElementException:
                print(f"Revenue data not found for address: {address}")
                result[address] = None

    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        return {"error": "WebDriver crashed!"}

    finally:
        driver.quit()  # Ensure the driver closes properly

    return result

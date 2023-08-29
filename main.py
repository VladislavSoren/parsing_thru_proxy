import os
import time

import requests
from requests.auth import HTTPBasicAuth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from db_functions import get_table
from functions_secondary import create_driver

from dotenv import load_dotenv, find_dotenv
import os

# Конфиденциальные данные
load_dotenv(find_dotenv())  # погрузка .env


def auth_facebook_via_selenium(website):
    proxies_df = get_table('facebook.db', 'proxies')
    proxies = proxies_df['proxy'].values

    for proxy in proxies:

        try:
            driver = create_driver(proxy)
            driver.get(website)
        except:
            continue

        empty_page_html = '<html><head></head><body></body></html>'
        empty_str = ''
        print(driver.page_source)
        if driver.page_source in (empty_page_html, empty_str):
            continue
        else:
            break

    # authorization
    # fill email
    email_field = driver.find_element(By.NAME, "email")
    email_field.clear()
    email_field.send_keys(FACEBOOK_EMAIL)
    time.sleep(1)

    # fill email
    pass_field = driver.find_element(By.NAME, "pass")
    pass_field.clear()
    pass_field.send_keys(FACEBOOK_PASS)
    time.sleep(1)

    # pass_field.send_keys(Keys.ENTER)

    loginbutton = driver.find_element(By.NAME, "login")
    loginbutton.click()
    time.sleep(1)

    driver.close()
    driver.quit()


if __name__ == '__main__':
    FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL')
    FACEBOOK_PASS = os.getenv('FACEBOOK_PASS')

    url_root = 'https://www.facebook.com'
    url = 'https://www.facebook.com/groups/itpeopleconnection/members'
    LOGIN_URL = "https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&amp;refid=8"

    auth_facebook_via_selenium(LOGIN_URL)

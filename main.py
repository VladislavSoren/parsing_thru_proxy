import os
import random
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from db_functions import get_table, create_table, drop_table
from functions_secondary import create_driver

from dotenv import load_dotenv, find_dotenv

# Конфиденциальные данные
load_dotenv(find_dotenv())  # погрузка .env


class StatusClass:
    Success = 'Success'
    Failed = 'Failed'


def fill_field(driver, by, name, value):
    email_field = driver.find_element(by, name)
    email_field.clear()
    email_field.send_keys(value)


def click_element(driver, by, name):
    loginbutton = driver.find_element(by, name)
    loginbutton.click()


def get_driver_with_alive_proxy(login_url, headless_mode):
    proxies_df = get_table('facebook.db', 'proxies')
    proxies = list(proxies_df['proxy'].values)
    random.shuffle(proxies)
    driver = None

    for proxy in proxies:

        try:
            driver = create_driver(headless=headless_mode, proxy=proxy)
            driver.get(login_url)
        except:
            continue

        empty_page_html = '<html><head></head><body></body></html>'
        empty_str = ''
        # print(driver.page_source)
        if driver.page_source in (empty_page_html, empty_str):
            continue
        else:
            break

    if driver is None:
        print('all proxies is bad')
        return driver
    return driver


def auth_facebook_via_selenium(driver):
    # fill email
    fill_field(driver, By.NAME, "email", FACEBOOK_EMAIL)
    time.sleep(1)

    # fill pass
    fill_field(driver, By.NAME, "pass", FACEBOOK_PASS)
    time.sleep(1)

    # click login button
    click_element(driver, By.NAME, "login")


def scroll_and_wait(driver, SCROLL_PAUSE_TIME):
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)


def scroll_to_end_of_the_page(driver, scroll_timeout_minute=1):
    SCROLL_PAUSE_TIME = 0.5
    scroll_timeout = time.time() + 60 * scroll_timeout_minute

    # Get scroll height
    driver.find_element(By.XPATH, "//html").click()  # trigger page (by default it is gray)
    last_height = driver.execute_script("return document.body.scrollHeight")

    scroll_count = 0
    while True:
        scroll_count += 1
        print(f'___Scroll_{scroll_count}')

        # Scroll down
        scroll_and_wait(driver, SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height or time.time() > scroll_timeout:
            break
        last_height = new_height


def get_scraped_users_info_lists(driver, target_url):
    # go to target_url
    driver.get(target_url)
    time.sleep(10)

    # Scroll to end of the page
    scroll_to_end_of_the_page(driver)

    users_block_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/div[8]/div/div[2]/div'
    users_block_obj = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, users_block_XPATH)))

    users_block_HTML = users_block_obj.get_attribute('innerHTML')
    bsObj = BeautifulSoup(users_block_HTML, 'html.parser')

    # parsing users data from html users block
    class_name_block_user_prof_url_and_name = 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f'
    users_prof_url_and_name = bsObj.find_all('a', class_=class_name_block_user_prof_url_and_name)
    users_name_list = []
    users_profile_urls_list = []
    for user_prof_url_and_name in users_prof_url_and_name:
        users_name_list.append(user_prof_url_and_name.text)
        users_profile_urls_list.append(user_prof_url_and_name['href'])

    users_image_url = users_images = bsObj.find_all('image')
    users_image_url_list = []
    for user_image_url in users_image_url:
        users_image_url_list.append(user_image_url['xlink:href'])

    return users_name_list, users_profile_urls_list, users_image_url_list


def save_data_to_db(users_name_list, users_profile_urls_list, users_image_url_list):
    users_info_df = pd.DataFrame(
        {
            'user_name': users_name_list,
            'user_profile_url': users_profile_urls_list,
            'user_image_url': users_image_url_list}
    )
    try:
        create_table(name_db, name_table, users_info_df)
    except ValueError:
        drop_table(name_db, name_table)
        create_table(name_db, name_table, users_info_df)


def get_users_info(login_url, target_url, headless_mode):
    driver = get_driver_with_alive_proxy(login_url, headless_mode)

    if driver is None:
        return 'failed to get data'

    auth_facebook_via_selenium(driver)
    time.sleep(10)

    users_name_list, users_profile_urls_list, users_image_url_list = get_scraped_users_info_lists(driver, target_url)

    save_data_to_db(users_name_list, users_profile_urls_list, users_image_url_list)

    driver.close()
    driver.quit()


if __name__ == '__main__':
    FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL')
    FACEBOOK_PASS = os.getenv('FACEBOOK_PASS')
    name_db = 'facebook.db'
    name_table = 'users_info'

    url_root = 'https://www.facebook.com'
    target_url = 'https://www.facebook.com/groups/itpeopleconnection/members'

    # found on stackoverflow, only with this link auth can be successful
    LOGIN_URL = "https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&amp;refid=8"

    status = None
    for _ in range(10):
        try:
            get_users_info(LOGIN_URL, target_url, headless_mode=False)
            print(StatusClass.Success)
        except:
            print(StatusClass.Failed)
            time.sleep(5)
            continue
        else:
            users_info_df = get_table(name_db, name_table)
            print(users_info_df)
            print(f'Number of users in table: {users_info_df}')
            break

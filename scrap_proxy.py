from threading import Thread

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from db_functions import create_table, get_table, insert_row, drop_table
from functions_secondary import log_time, create_driver, get_parsing_indexes, execute_threads
from log_pars_config import parsing_logger


def proxy_is_alive(proxy, timeout=5):
    try:
        requests.get("https://www.google.com/",
                     proxies={
                         "http": "http://" + proxy,
                         "https": "http://" + proxy,
                     },
                     timeout=timeout)
    except Exception as x:
        return False

    return True


def get_proxies_list(driver):
    users_block_obj = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.TAG_NAME, 'body')))

    users_block_HTML = users_block_obj.get_attribute('innerHTML')
    bsObj = BeautifulSoup(users_block_HTML, 'html.parser')

    proxies_str = bsObj.textarea.text.split('\n\n')[1].strip('\n')
    proxies_list = proxies_str.split('\n')

    return proxies_list


def worker_check_and_save_proxies(
        proxies_list,
        worker_i, start_i, end_i,
        timeout_alive_checking,
        only_alive=True, stop_process=None
):
    # checking proxies
    for index in range(start_i, end_i):
        proxy = proxies_list[index]

        # Condition of stopping parser
        if (stop_process == worker_i) or (stop_process == 'stop_all'):
            parsing_logger.info(f'!!!!!!!___w_{worker_i} ОСТАНОВЛЕН!!!')
            break

        # add alive proxy to bd
        if only_alive and proxy_is_alive(proxy, timeout=timeout_alive_checking):
            row = (worker_i, index, proxy)
            insert_row(name_db, name_table, row)
            parsing_logger.info(f'{index} -- {proxy} is ALIVE in worker_{worker_i}')


@log_time(logger=parsing_logger)
def scrap_proxies():
    timeout_alive_checking = 10

    driver = create_driver(headless_mode)
    driver.get(website)

    proxies_list = get_proxies_list(driver)

    # get indexes for workers (0 - first index of list, "total_proxies - 1" - for proper count)
    parsing_indexes = get_parsing_indexes(0, total_proxies - 1, count_of_workers)

    # Creation thread group
    Threads = [Thread(target=worker_check_and_save_proxies, args=(
        proxies_list,
        worker_i,
        parsing_indexes[worker_i], parsing_indexes[worker_i + 1],
        timeout_alive_checking,
        name_db, name_table, parsing_logger))
               for worker_i in range(count_of_workers)
               ]

    execute_threads(Threads, parsing_logger)

    driver.close()
    driver.quit()

    return 'Ready'


if __name__ == '__main__':
    website = 'https://free-proxy-list.net/'
    total_proxies = 300
    count_of_workers = 30
    name_db = 'facebook.db'
    name_table = 'proxies'
    with_workers = False
    headless_mode = True

    # create table fo proxies
    proxies_df = pd.DataFrame({'worker_id': [], 'proxy_id': [], 'proxy': []})
    try:
        create_table(name_db, name_table, proxies_df)
    except ValueError:
        drop_table(name_db, name_table)
        create_table(name_db, name_table, proxies_df)

    status = scrap_proxies()
    if status: print('Ready!')

    proxies_df = get_table('facebook.db', 'proxies')

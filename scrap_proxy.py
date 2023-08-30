from threading import Thread

import pandas as pd
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from db_functions import create_table, get_table, insert_row, drop_table
from functions_secondary import log_time, create_driver, get_parsing_indexes
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


def get_host_port(driver, index, timeout=5):
    host = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section[1]/div/div[2]/div/table/tbody/tr[{index}]/td[1]'))
    ).text
    port = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, f'/html/body/section[1]/div/div[2]/div/table/tbody/tr[{index}]/td[2]'))
    ).text
    return host, port


def worker_scrap(
        website,
        worker_i, start_i, end_i,
        name_db, name_table,headless_mode,
        only_alive=True, stop_process=None
):
    # timeouts
    timeout_proxy_parsing = 5
    timeout_alive_checking = 10

    driver = create_driver(headless_mode)
    driver.get(website)

    # Parsing proxies
    for index in range(start_i, end_i):

        print(index)

        # Condition of stopping parser
        if (stop_process == worker_i) or (stop_process == 'stop_all'):
            parsing_logger.info(f'!!!!!!!___w_{worker_i} ОСТАНОВЛЕН!!!')
            break

        # receiving host and port (proxy)
        host, port = get_host_port(driver, index, timeout=timeout_proxy_parsing)
        proxy = ':'.join([host, port])

        # add alive proxy to bd
        if only_alive and proxy_is_alive(proxy, timeout=timeout_alive_checking):
            row = (worker_i, index, proxy)
            insert_row(name_db, name_table, row)
            parsing_logger.info(f'{index} -- {proxy} is ALIVE in worker_{worker_i}')

    # close page and driver
    driver.close()
    driver.quit()


@log_time(logger=parsing_logger)
def scrap_proxy_selenium(website, total_proxies, count_of_workers, name_db, name_table,
                         headless_mode):
    parsing_indexes = get_parsing_indexes(1, total_proxies + 1, count_of_workers)

    # Creation thread group
    Threads = [Thread(target=worker_scrap, args=(
        website,
        worker_i,
        parsing_indexes[worker_i], parsing_indexes[worker_i + 1],
        name_db, name_table, headless_mode))
               for worker_i in range(count_of_workers)
               ]

    # .........Starting threads.........
    for t in Threads:
        t.start()

    # .........Check if threads are alive
    for t in Threads:
        if t.is_alive():
            parsing_logger.info(f'Thread №{t} ALIVE')
        else:
            parsing_logger.info(f'Thread №{t} DEAD')

    # .........Waiting for all threads to complete
    for t in Threads:
        t.join()

    # .........Checking for all threads to complete
    for t in Threads:
        if t.is_alive():
            parsing_logger.info(f'Thread №{t} ALIVE')
        else:
            parsing_logger.info(f'Thread №{t} DEAD')

    return 'Ready'


if __name__ == '__main__':
    website = 'https://free-proxy-list.net/'
    total_proxies = 300
    count_of_workers = 15
    name_db = 'facebook.db'
    name_table = 'proxies'
    headless_mode = True

    # create table fo proxies
    proxies_df = pd.DataFrame({'worker_id': [], 'proxy_id': [], 'proxy': []})
    try:
        create_table(name_db, name_table, proxies_df)
    except ValueError:
        drop_table(name_db, name_table)
        create_table(name_db, name_table, proxies_df)

    status = scrap_proxy_selenium(website, total_proxies, count_of_workers, name_db, name_table,
                                  headless_mode)
    if status: print('Ready!')

    proxies_df = get_table('facebook.db', 'proxies')

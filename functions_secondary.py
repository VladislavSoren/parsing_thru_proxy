from selenium import webdriver
import math
import time
from functools import wraps


# Функция получения интервала range для парсинга (согласно данному range будут раздваться индексы воркерам(ботам))
def get_parsing_indexes(start_ind, end_ind, count_bot):
    count_record = (end_ind - start_ind) + 1
    print(count_record)
    part = count_record / count_bot
    part = math.ceil(part)
    return range(start_ind, start_ind + part * (count_bot + 1), part)


# Функция получения драйвера по url страницы
def create_driver():
    # WEB_DRIVER_PATH = 'Drivers/geckodriver-v0.32.2-win-aarch64/geckodriver'  # Later in environment variable!
    WEB_DRIVER_PATH = 'Drivers/chromedriver/chromedriver'  # Later in environment variable!
    # options
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # options.headless = True
    driver = webdriver.Chrome(executable_path=WEB_DRIVER_PATH,
                                options=chrome_options)
    return driver


# Функция декоратор замера времени выполнения функции
def log_time(logger, description=''):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.info(f'Start parsing {description} ({func.__name__})')
            result = func(*args, **kwargs)
            end = time.time()
            exec_time = round(end - start, 2)
            logger.info(f'Parsing time {description} ({func.__name__}): {exec_time}s')
            return result
        return wrapper
    return inner








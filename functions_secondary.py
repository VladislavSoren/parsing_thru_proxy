from selenium import webdriver
import math
import time
from functools import wraps


# Функция получения интервала range для парсинга (согласно данному range будут раздваться индексы воркерам(ботам))
def get_parsing_indexes(start_ind, end_ind, count_bot):
    count_record = (end_ind - start_ind) + 1
    print(f'Количество записей для парсинга: {count_record}')
    part = count_record / count_bot
    part = math.ceil(part)
    return range(start_ind, start_ind + part * (count_bot + 1), part)


# Функция получения драйвера по url страницы
def create_driver(headless=True, proxy=False):
    # WEB_DRIVER_PATH = 'Drivers/geckodriver-v0.32.2-win-aarch64/geckodriver'  # Later in environment variable!
    WEB_DRIVER_PATH = 'Drivers/chromedriver/chromedriver'  # Later in environment variable!
    # options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("window-size=1920,1080")

    # When the sandbox is disabled using the flag option --no-sandbox, websites or rendered pages
    # can potentially execute malicious Javascript based exploits on your computer.
    # chrome_options.add_argument('--no-sandbox')

    # browser window wouldn’t be visible
    if headless:
        chrome_options.add_argument('--headless')

    # Only added when CI system environment variable is set or when inside a docker instance.
    # chrome_options.add_argument('--disable-dev-shm-usage')

    # server requisites
    # chrome_options.add_argument("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    # my PC requisites
    chrome_options.add_argument(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')

    # after adding this block "https://intoli.com/" makes available (WebDriver - present (failed))
    # check form: https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # after adding this block "https://intoli.com/" makes available (WebDriver - missing (passed))
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if proxy:
        chrome_options.add_argument('--proxy-server=%s' % proxy)

    # options.headless = True
    driver = webdriver.Chrome(executable_path=WEB_DRIVER_PATH,
                              options=chrome_options)
    return driver


def execute_threads(Threads, parsing_logger):
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

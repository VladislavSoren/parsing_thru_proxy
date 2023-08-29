import os

import requests
from requests.auth import HTTPBasicAuth

from db_functions import get_table


def get_alive_proxy_list():
    directory = 'Proxies'

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            print(f)


def get_facebook_response(url, auth, timeout):
    proxies_df = get_table('facebook.db', 'proxies')
    proxies = proxies_df['proxy'].values
    resp = 'None'

    for proxy in proxies:
        try:
            resp = requests.get(url,
                                proxies={
                                    "http": "http://" + proxy,
                                    "https": "http://" + proxy,
                                },
                                auth=auth,
                                timeout=timeout)
            if resp.status_code == 200:
                print(proxy)
                print(resp)
                break
        except:
            continue

    return resp


if __name__ == '__main__':
    FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL')
    FACEBOOK_PASS = os.getenv('FACEBOOK_PASS')

    url_root = 'https://www.facebook.com'
    url = 'https://www.facebook.com/groups/itpeopleconnection/members'

    auth = HTTPBasicAuth(FACEBOOK_EMAIL, FACEBOOK_PASS)
    get_facebook_response(url, auth, timeout=10)

    pass

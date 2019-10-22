import requests
import json

from config import RETRY_MAX, OK_CNT, TIMEOUT, CHECK_URL, INFILENAME

def check(port=1080):
    proxy = f'127.0.0.1:{port}'
    proxies = {'http': 'socks5://' + proxy,
               'https': 'socks5://' + proxy
               }

    cnt = 0
    # CHECK_URL = 'http://www.google.com'
    for i in range(1, RETRY_MAX + 1):
        print(f'第{i}次验证')
        try:
            response = requests.get(CHECK_URL, proxies=proxies, timeout=TIMEOUT)
            # print(response.text)
            cnt += 1
        except requests.exceptions.ConnectionError as e:
            print('Error', e.args)
        except requests.exceptions.ReadTimeout as e:
            print('Error', e.args)

    print(f'验证{RETRY_MAX}次， 通过{cnt}次')
    if cnt >= OK_CNT:
        print('验证通过')
        return True
    else:
        print('验证失败')
        return False


def readJson():
    with open(INFILENAME) as load_f:
        configDict = json.load(load_f)
        print(configDict)


if __name__ == '__main__':
    # check()
    pass
    readJson()

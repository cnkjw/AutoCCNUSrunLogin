# ！/bin/python3
# -*- coding: utf-8 -*-

from tenacity import retry, stop_after_attempt, wait_fixed
import requests
from urllib.request import urlopen
import time

# ==========================================================
# 设置登录所用账号
my_username = "username"
my_passwd = "passwd"

# 重试间隔
retry_interval = 30  # second
# ----------------------------------------------------------


def get_csrf_token():
    csrf_url = "https://portal.ccnu.edu.cn/api/csrf-token"
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'Priority': 'u=5, i',
    }

    response = requests.get(url=csrf_url, headers=headers)

    return (
        requests.utils.dict_from_cookiejar(response.cookies),
        eval(response.text)['csrf_token'],
    )


def login(csrf_token, cookiesdict):
    url = 'https://portal.ccnu.edu.cn/api/account/login'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT': '1',
        'Origin': 'https://portal.ccnu.edu.cn',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'X-Csrf-Token': csrf_token,
    }

    data_raw = {'username': f'{my_username}', 'password': f'{my_passwd}', 'nasId': '3'}
    cookies = {'yudear': cookiesdict['yudear']}

    response = requests.post(url, headers=headers, cookies=cookies, data=data_raw)

    return response


def internet_online():
    try:
        urlopen('https://www.baidu.com/', timeout=10)
        return True
    except:
        return False


@retry(stop=stop_after_attempt(5), wait=wait_fixed(3), reraise=True)
def connect():
    cookiesdict, csrf_token = get_csrf_token()
    response = login(csrf_token, cookiesdict)
    return response.text


def now_time():
    # Get the current time in seconds since the epoch
    current_time_seconds = time.time()
    # Convert the seconds to a struct_time object
    current_time_struct = time.localtime(current_time_seconds)
    # Format the time as a string
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time_struct)
    return formatted_time

if __name__ == "__main__":
    print(f"[{now_time()}] 自动联网脚本启动...")
    while True:
        time.sleep(retry_interval)
        if internet_online():
            continue
        msg = connect()
        print(f'[{now_time()}] {msg}')
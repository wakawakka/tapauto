import os
import code
import time
import json
import tempfile
import subprocess
import logging
import asyncio
import base64
from distutils.dir_util import copy_tree
import urllib.parse as up

import notpixel_tools
from secure_browser import SecFirefoxBrowser, SecChromeBrowser
from selenium.webdriver.common.by import By
from telegram_utils import Telega


def run_tonswap_browser(number, tdatas_base_path, browser=True, open_url=True, sleep_time=1.488):
    num_path = os.path.join(tdatas_base_path, number)
    original_tdata_path = os.path.join(num_path, 'tdata')

    assert 'proxy.txt' in os.listdir(num_path)
    print(os.path.join(num_path, 'proxy.txt'))
    with open(os.path.join(num_path, 'proxy.txt')) as f:
        cntnt = f.read()
    proxy = cntnt.split('\n')[0]
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    t = Telega(
        telegram_cache_dir="tdatas",
        session_id=number,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        logfile_path="tdatas/common.log",
        logging_level=logging.DEBUG,
    )

    password = None
    if "Twofa.txt" in os.listdir(num_path):
        password = open(os.path.join(num_path, "Twofa.txt")).read()

    async def async_sosalnya():
        await t.init_client_tdata(
            tdata_path=original_tdata_path,
            platform="macos",
            hardware_id=number,
            password=password,
        )
        url = await t.get_bot_webapp_noapp("tapswap_bot", "android")
        #url = await t.get_bot_webapp("notpx_bot", "android")
        return url
    url = asyncio.run(async_sosalnya())

    print('URL TO OPEN:')
    print(url)
    if browser:
        sb = SecFirefoxBrowser(proxy_host, proxy_port, proxy_user, proxy_password, wire=False)
        if open_url:
            sb.browser.get(url)
        return sb.browser


if __name__ == '__main__':
    number = '27632528538'


    tdatas_base_path = r'C:\Users\gleb\Projects\tapauto\tdatas'
    #tgportable_template_path = r'C:\Users\gburgerfuck\Desktop\TELEGRAMZ\tportable-template'
    #keep_dir = r'C:\Users\gburgerfuck\Desktop\TELEGRAMZ'

    # run_tgportable(number, tdatas_base_path, tgportable_template_path, keep_dir)
    run_tonswap_browser(number, tdatas_base_path, open_url=True)
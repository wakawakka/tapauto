import os
import tempfile
import subprocess
import logging
import asyncio
from distutils.dir_util import copy_tree

import notpixel_tools
from secure_browser import SecFirefoxBrowser
from telegram_utils import Telega



def run_tgportable(number, tdatas_base_path, tgportable_template_path, keep_dir):
    num_path = os.path.join(tdatas_base_path, number)
    original_tdata_path = os.path.join(num_path, 'tdata')
    tgportable_num_path = os.path.join(keep_dir, number)
    tgportable_tdata_path = os.path.join(tgportable_num_path, r'Telegram\tdata')
    tgportable_config_path = os.path.join(tgportable_num_path, 'proxychains.conf')
    tgportable_tgexe_path = os.path.join(tgportable_num_path, 'Telegram\Telegram.exe')

    assert 'proxy.txt' in os.listdir(num_path)

    with open(os.path.join(num_path, 'proxy.txt')) as f:
        cntnt = f.read()
    proxy = cntnt.split('\n')[0]

    copy_tree(tgportable_template_path, tgportable_num_path)
    copy_tree(original_tdata_path, tgportable_tdata_path)

    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    with open(tgportable_config_path, 'a') as f:
        f.write(f"socks5 {proxy_host} {proxy_port} {proxy_user} {proxy_password}")
    
    pc_exe_path = os.path.join(keep_dir, 'pc\pc.exe')
    print(f"{pc_exe_path} -f {tgportable_config_path} {tgportable_tgexe_path}")
    subprocess.run(f"{pc_exe_path} -f {tgportable_config_path} {tgportable_tgexe_path}", shell=True, check=True)
    print('FINISH')

def run_notpixels_browser(number, tdatas_base_path):
    num_path = os.path.join(tdatas_base_path, number)
    original_tdata_path = os.path.join(num_path, 'tdata')

    assert 'proxy.txt' in os.listdir(num_path)
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
        url = await t.get_bot_webapp("notpx_bot", "android")
        return url
    url = asyncio.run(async_sosalnya())

    sb = SecFirefoxBrowser(proxy_host, proxy_port, proxy_user, proxy_password)
    sb.browser.get(url)
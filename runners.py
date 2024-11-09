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



def run_tgportable(number, tdatas_base_path, tgportable_template_path, keep_dir):
    num_path = os.path.join(tdatas_base_path, number)
    original_tdata_path = os.path.join(num_path, 'tdata')
    tgportable_num_path = os.path.join(keep_dir, number)
    tgportable_tdata_path = os.path.join(tgportable_num_path, r'Telegram\tdata')
    tgportable_config_path = os.path.join(tgportable_num_path, r'proxychains.conf')
    tgportable_tgexe_path = os.path.join(tgportable_num_path, r'Telegram\Telegram.exe')

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
    
    pc_exe_path = os.path.join(keep_dir, r'pc\pc.exe')
    print(f"{pc_exe_path} -f {tgportable_config_path} {tgportable_tgexe_path}")
    subprocess.run(f"{pc_exe_path} -f {tgportable_config_path} {tgportable_tgexe_path}", shell=True, check=True)
    print('FINISH')

def make_desktop(url):
    pr = up.urlparse(url)
    tgWebAppData = up.parse_qs(pr.fragment)['tgWebAppData'][0]
    initData = base64.b64encode(tgWebAppData.encode()).decode()
    return 'https://app.notpx.app/stars?initData=' + initData

    

def run_notpixels_browser(number, tdatas_base_path, browser=True, open_url=True, desktop=True, sleep_time=1.488):
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
        url = await t.get_bot_webapp("notpx_bot", "android")
        return url
    url = asyncio.run(async_sosalnya())
    if desktop:
        url = make_desktop(url)
        print('UPDATED TO DESKTOP')
    print('URL TO OPEN:')
    print(url)
    if browser:
        sb = SecFirefoxBrowser(proxy_host, proxy_port, proxy_user, proxy_password, wire=False)
        if open_url:
            sb.browser.get(url)
        return sb.browser

def registrate_tonkeeper(number, tdatas_base_path, sleep_time=1.488):
    browser = run_notpixels_browser(number, tdatas_base_path)
    browser.implicitly_wait(10)
    time.sleep(sleep_time + 5)
    browser.find_element(By.XPATH, "//button[text() = 'Let’s Gooooooo!']").click()
    time.sleep(sleep_time)
    sb_el = browser.find_elements(By.XPATH, "//button[contains(@class, 'stars_button')]")
    print('len(sb_el)', len(sb_el))
    sb_el[1].click()
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//button[text() = 'Connect wallet']").click()
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//img[@src = 'https://tonkeeper.com/assets/tonconnect-icon.png']/../..").click()
    time.sleep(sleep_time)
    #rs = browser.requests
    #urls = [r.url for r in browser.requests]
    ton_storage = browser.execute_script("return window.localStorage.getItem(arguments[0]);", "ton-connect-storage_bridge-connection")
    pub_key = json.loads(ton_storage)['sessionCrypto']['publicKey']
    pars = {
        'v': 2,
        'id': pub_key,
        'r': {"manifestUrl": "https://app.notpx.app/tonconnect-manifest.json","items":[{"name":"ton_addr"}]},
        'ret': 'none',
    }
    tonkeeper_url = 'https://app.tonkeeper.com/ton-connect?' + up.urlencode(pars)
    browser.get(tonkeeper_url)
    time.sleep(sleep_time + 3)
    browser.find_element(By.XPATH, "//a[contains(text(), 'Sign in with Tonkeeper Web')]").click()
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Get started')]").click()
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//button/div/span[contains(text(), 'New Wallet')]").click()
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    time.sleep(sleep_time)

    words_el = browser.find_elements(By.XPATH, "//div[@wordsnumber = '24']/span")
    assert len(words_el) == 24
    words = [el.text for el in words_el]
    num_path = os.path.join(tdatas_base_path, number)
    words_path = os.path.join(num_path, 'words.txt')
    assert not os.path.exists(words_path)
    with open(words_path, 'w') as f:
        f.write('\n'.join(words))
    time.sleep(sleep_time)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    time.sleep(sleep_time)
    
    check_numbers = [int(el.text.strip(':')) for el in browser.find_elements(By.XPATH, "//label/input/../span")]
    check_words = [words[i-1].split('.')[1].strip() for i in check_numbers]
    for input_el, word in zip(browser.find_elements(By.XPATH, "//label/input"), check_words):
        input_el.send_keys(word)
        time.sleep(1)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    time.sleep(sleep_time)

    pass_inputs = browser.find_elements(By.XPATH, "//input[@type='password']")
    for pi in pass_inputs:
        pi.send_keys('228Adidas228')
        time.sleep(1)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    browser.find_element(By.XPATH, "//button[contains(text(), 'Save')]").click()
    time.sleep(sleep_time)
    
    code.interact(local=locals())

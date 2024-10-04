from hashlib import md5
import time
import random
import io
import os
import re
from urllib.parse import unquote

import requests
from PIL import Image
import numpy as np
from selenium.webdriver.common.by import By
from retry import retry

import localsettings
import settings
import telegram_utils_new
import secure_browser
import notpixel_tools


class PixelActions:
    def __init__(
        self,
        web_app_entry_url,
        proxy=False,
        proxy_host="",
        proxy_port=0,
        proxy_user="",
        proxy_password="",
    ):
        self.web_app_entry_url = web_app_entry_url
        self.energy = 0
        self.auth_token = self.get_autorization_header(web_app_entry_url)
        self.requests_proxy = None
        if proxy:
            self.requests_proxy = {
                "http": f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
                "https": f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
            }

        self.sb = secure_browser.Browser(
            proxy=proxy,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
            proxy_password=proxy_password,
        )

    def gui_app_start(self):
        self.sb.browser.get(self.web_app_entry_url)

    def gui_click_initial_buttons(self):
        button_texts = ["Okay", "Gooooo"]
        okay_button = True
        while okay_button:
            clicked = False
            for bp in button_texts:
                okay_button = self.sb.find_element(
                    By.XPATH, f'//div/button[contains(text(), "{bp}")]', delay=5
                )
                if okay_button:
                    okay_button_text = None
                    try:
                        okay_button_text = okay_button.text
                        print(f"Found Okay button: {okay_button_text}")
                        okay_button.click()
                        clicked = True
                    except:
                        print(f"Found unclickable Okay button: {okay_button_text}")
            if clicked:
                okay_button = True

    def get_autorization_header(self, web_app_url):
        q, w = web_app_url.split("#tgWebAppData=")
        a, s = w.split("&", 1)
        return unquote(a)

    def get_headers_api(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.9;q=0.9",
            "Authorization": f"initData {self.auth_token}",
            "Sec-Fetch-Dest": "empty",
            "sec-fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36",
            "Referer": "https://app.notpx.app/",
            "Priority": "u=1, i",
            "Origin": "https://app.notpx.app",
            "Referer": "https://app.notpx.app/",
        }

    @retry(tries=3, delay=10)
    def claim(self):
        browser_url = "https://app.notpx.app/claiming"
        if self.sb.browser.current_url != browser_url:
            self.sb.browser.get(browser_url)
        url = "https://notpx.app/api/v1/mining/claim"
        headers = self.get_headers_api()
        r = requests.get(url, headers=headers, proxies=self.requests_proxy)
        if r.status_code == 200:
            data = r.json()
            time.sleep(random.randint(5, 8))
            print(f"Successfull claimed reward. Status: {r.status_code}")
            return data.get("activated")
        else:
            print(
                f"Failed to claim collected tokens. Status: {r.status_code}, Error: {r.text}"
            )
            return False

    @retry(tries=3, delay=10)
    def upgrade_boost(self, key):
        url = f"https://notpx.app/api/v1/mining/boost/check/{key}"
        headers = self.get_headers_api()
        r = requests.get(url, headers=headers, proxies=self.requests_proxy)
        time.sleep(random.randint(5, 8))
        if r.status_code == 200:
            print(f"Successfull upgrade {key}. Status: {r.status_code}")
            return True
        else:
            print(
                f"Failed to install upgrade. Status: {r.status_code}, Error: {r.text}"
            )
            return False

    def install_upgrades(self, balance, boosts):
        browser_url = "https://app.notpx.app/claiming"
        if self.sb.browser.current_url != browser_url:
            self.sb.browser.get(browser_url)
        energy_limit_current_level = boosts.get("energyLimit")
        energy_limit_upgrade_price = settings.upgrade_charge_count.get(
            energy_limit_current_level + 1
        )

        paint_reward_current_level = boosts.get("paintReward")
        paint_reward_upgrade_price = settings.upgrade_repaint_price.get(
            paint_reward_current_level + 1
        )

        recharge_speed_curent_level = boosts.get("reChargeSpeed")
        recharge_speed_upgrade_price = settings.upgrade_charge_restoration_price.get(
            recharge_speed_curent_level + 1
        )

        if balance > recharge_speed_upgrade_price:
            res = self.upgrade_boost("reChargeSpeed")
            if res:
                balance -= recharge_speed_upgrade_price

        if balance > paint_reward_upgrade_price:
            res = self.upgrade_boost("paintReward")
            if res:
                balance -= paint_reward_upgrade_price

        if balance > energy_limit_upgrade_price:
            res = self.upgrade_boost("energyLimit")
            if res:
                balance -= energy_limit_upgrade_price

    @retry(tries=3, delay=10)
    def get_acc_status(self):
        browser_url = "https://app.notpx.app/claiming"
        if self.sb.browser.current_url != browser_url:
            self.sb.browser.get(browser_url)
        url = "https://notpx.app/api/v1/mining/status"
        headers = self.get_headers_api()
        r = requests.get(url, headers=headers, proxies=self.requests_proxy)

        if r.status_code == 200:
            data = r.json()
            charges = data.get("charges")
            recharge_speed = data.get("reChargeSpeed", 0) / 1000  # in sec
            max_charges = data.get("maxCharges", 0)

            balance = data.get("userBalance")
            claimed = data.get("claimed")
            if claimed == 0:
                claimed = self.claim()
            boosts = data.get("boosts", {})
            if boosts:
                self.install_upgrades(balance=balance, boosts=boosts)

            time.sleep(random.randint(5, 8))
            return {
                "charges": charges,
                "charge_restore_speed": recharge_speed,
                "max_charges": max_charges,
                "balance": balance,
            }
        else:
            print(
                f"Failed to get account status. Status: {r.status_code}, Error: {r.text}"
            )
            return False

    @retry(tries=3, delay=10)
    def paint_pixel(self, x: int, y: int, color: tuple):
        browser_url = "https://app.notpx.app/"
        if self.sb.browser.current_url != browser_url:
            self.sb.browser.get(browser_url)
        url = "https://notpx.app/api/v1/repaint/start"
        color_s = notpixel_tools.rgb_to_hex(color)
        # if len(color_s) != 7 or not re.match("#[ABCDEF0123456789]{6}", color_s):
        #     print("Bad color format, try #00FFAA")
        #     return False
        headers = self.get_headers_api()
        pixel_id = y * 1000 + x + 1
        r = requests.post(
            url,
            headers=headers,
            json={"pixelId": pixel_id, "newColor": color_s},
        )
        if r.status_code == 200:
            print(f"Pixel {x}:{y} painted to {color_s}")
            time.sleep(random.randint(5, 8))
            return r.json()
        else:
            print(f"Failed to paint pixel. Status: {r.status_code}, Error: {r.text}")
            return False

    def paint(self, pixels_to_paint):
        painted = []
        for x, y, task_pix_color in pixels_to_paint:
            if self.energy < 1:
                return painted
            ret = None
            try:
                ret = self.paint_pixel(x, y, task_pix_color)
                ret_balance = ret.get("balance")
                if ret_balance:
                    painted.append((x, y))
                    self.energy -= 1
            except:
                print(f"Falied to draw pix {x}:{y}. Ret: {ret}")

        return painted

    def run(self, pixels_to_paint):
        self.gui_app_start()
        self.gui_click_initial_buttons()
        acc_state = self.get_acc_status()
        charges = acc_state.get("charges", 0)
        if charges > 0:
            self.energy = charges
        recharge_speed = acc_state.get("charge_restore_speed", 0)
        max_charges = acc_state.get("max_charges", 0)

        painted = self.paint(pixels_to_paint)
        charges_restore_ts = int(
            time.time() + recharge_speed * (max_charges - self.energy)
        )
        return {
            "painted": painted,
            "charges": self.energy,
            "charges_full_restore_in": charges_restore_ts,
        }


# for i in range(1, 6):
#     paint_pixel(i, 80, "#FFC0CB", auth_token=auth_token)
# # mb.browser.get("https://browserleaks.com/javascript")
# pass


if __name__ == "__main__":
    from tasks import tasks

    bot_username = "notpx_bot"
    app_url = "https://app.notpx.app"

    webapp_login_url = telegram_utils_new.get_bot_webapp_url(bot_username, app_url)
    pa = PixelActions(
        webapp_login_url,
        proxy=False,
        proxy_host="",
        proxy_port=8000,
        proxy_user="",
        proxy_password="",
    )
    task = (
        (80, 80, (255, 141, 161)),
        (80, 81, (255, 141, 161)),
        (81, 80, (255, 141, 161)),
        (81, 81, (255, 141, 161)),
    )
    job_result = pa.run(task)
    print(job_result)
    # balance = pa.draw()

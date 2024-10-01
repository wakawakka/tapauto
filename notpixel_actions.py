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
import telegram_utils
import secure_browser


class PixelActions:
    # создаем этот класс, кидаем ему таск, он тратит все доступные пиксели, в этот момент себя качает
    # метод draw возвращает пиксели, которые ему удалось закрасить и выполнен ли на текущий момент таск полностью

    def __init__(self, web_app_entry_url, task):
        self.web_app_entry_url = web_app_entry_url
        self.task = task
        self.auth_token = self.get_autorization_header(web_app_entry_url)
        self.sb = secure_browser.Browser()

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

    @retry(tries=3, delay=5)
    def paint_pixel(self, x: int, y: int, color: str):
        color = color.upper()
        if len(color) != 7 or not re.match("#[ABCDEF0123456789]{6}", color):
            print("Bad color format, try #00FFAA")
            return False
        headers = {
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
        }

        pixel_id = y * 1000 + x + 1
        r = requests.post(
            "https://notpx.app/api/v1/repaint/start",
            headers=headers,
            json={"pixelId": pixel_id, "newColor": color},
        )
        time.sleep(random.randint(5, 8))
        if r.status_code == 200:
            print(f"Pixel {x}:{y} painted to {color}")
            return r.json()
        else:
            print(r.text)

    def rgb_to_hex(self, pix):
        r, g, b = pix
        r, g, b = int(r), int(g), int(b)
        # return hex((r << 16) + (g << 8) + b).replace('0x','#').upper()
        n = (r << 16) + (g << 8) + b
        return f"#{n:06X}"

    def get_image_state(self):
        image_url = "https://image.notpx.app/api/v2/image"
        r = requests.get(image_url)
        if r.status_code == 200:
            img_io = io.BytesIO(r.content)
            img_io.seek(0)
        else:
            print(
                f"Fail to get image state (get request). Status: {r.status_code}, Error: {r.text}"
            )
            return False
        img = Image.open(img_io)
        np_img = np.array(img)
        color_data = []
        for line in np_img:
            color_data.append([self.rgb_to_hex(pix) for pix in line])

        return color_data

    def draw(self):
        image_data = self.get_image_state()
        init_x, init_y = self.task["init_position"]
        art = self.task["art"]
        balance = 0
        drawed = []
        pixels_to_draw = []

        for y_pad, line in enumerate(art):
            for x_pad, task_pix_color in enumerate(line):
                task_pix_color = task_pix_color.upper()
                if not task_pix_color:
                    continue
                x, y = init_x + x_pad, init_y + y_pad
                if task_pix_color == image_data[y][x]:
                    print(f"Same same {x}:{y}")
                else:
                    print(f"Need paint {x}:{y}")
                    pixels_to_draw.append((x, y, task_pix_color))

        # random.shuffle(pixels_to_draw)

        # for x, y, task_pix_color in pixels_to_draw:
        #     try:
        #         ret = self.paint_pixel(x, y, task_pix_color)
        #         ret_balance = ret.get("balance")
        #         if ret_balance:
        #             balance = ret_balance
        #             drawed.append((x, y))
        #     except:
        #         print(f"Falied to draw pix {x}:{y}")

        return balance


# for i in range(1, 6):
#     paint_pixel(i, 80, "#FFC0CB", auth_token=auth_token)
# # mb.browser.get("https://browserleaks.com/javascript")
# pass


if __name__ == "__main__":
    from tasks import tasks

    bot_username = "notpx_bot"
    app_url = "https://app.notpx.app"

    webapp_login_url = telegram_utils.get_bot_webapp_url(bot_username, app_url)
    pa = PixelActions(webapp_login_url, tasks["taskid1"])
    pa.gui_app_start()
    pa.gui_click_initial_buttons()
    pa.draw()

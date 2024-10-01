from hashlib import md5
import time
import random
import io
import os
import re
from urllib.parse import unquote

import requests
from selenium.webdriver.common.by import By

import localsettings
import telegram_utils
import secure_browser

bot_username = "notpx_bot"
app_url = "https://app.notpx.app"


def get_autorization_header(web_app_url):
    q, w = web_app_url.split("#tgWebAppData=")
    a, s = w.split("&", 1)
    return unquote(a)


webapp_login_url = telegram_utils.get_bot_webapp_url(bot_username, app_url)
auth_token = get_autorization_header(web_app_url=webapp_login_url)

# создаем этот класс, кидаем ему таск, он тратит все доступные пиксели, в этот момент себя качает
# метод draw возвращает пиксели, которые ему удалось закрасить и выполнен ли на текущий момент таск полностью


class PixelActions:

    def __init__(self, auth_token, task):
        pass

    def paint_pixel(x: int, y: int, color: str, auth_token):
        color = color.upper()
        if len(color) != 7 or not re.match("#[ABCDEF0123456789]{6}", color):
            print("Bad color format, try #00FFAA")
            return False
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.9;q=0.9",
            "Authorization": f"initData {auth_token}",
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
        if r.status_code == 200:
            print(f"Pixel {x}:{y} painted to {color}")
        else:
            print(r.text)
        time.sleep(random.randint(5, 8))
        pass


sb = secure_browser.Browser()


sb.browser.get(webapp_login_url)

okay_button = True
button_texts = ["Okay", "Gooooo"]
while okay_button:
    clicked = False
    for bp in button_texts:
        okay_button = sb.find_element(
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

image_url = "https://image.notpx.app/api/v2/image"
for i in range(1, 6):
    paint_pixel(i, 80, "#FFC0CB", auth_token=auth_token)
# mb.browser.get("https://browserleaks.com/javascript")
pass

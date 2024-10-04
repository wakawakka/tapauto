from hashlib import md5
import time
import random
import io
import os
import re
import code
from urllib.parse import unquote

import requests
from PIL import Image
import numpy as np
from selenium.webdriver.common.by import By
from retry import retry

import settings
import telegram_utils
import secure_browser
import notpixel_tools
import notpixel_actions


if __name__ == '__main__':
    # ALL we should set about user (probably import from settings)
    root=r'C:\Users\gburgerfuck\Desktop\TELEGRAMZ'
    number='8801747034955'
    proxy_user="07196708-zone-custom-region-BD-sessid-jGLhrrfL-sessTime-120"



    proxy_host = "f.proxys5.net"
    proxy_port = 6200
    proxy_password = "6pGOVG0G"
    print(1)
    tg = telegram_utils.Telega(
        session_id=number,
        telegram_cache_dir=settings.telegram_cache,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
    )
    print(2)
    tdata_path = r"C:\Users\gburgerfuck\Downloads\8801747034955\tdata"#os.path.join(root, f"tportable-{number}", "Telegram", "tdata")
    tg.init_client_tdata(tdata_path, platform="desktop", hardware_id="228", password=None)
    print(3)
    app_url = tg.get_bot_webapp(
            bot_username="notpixel",
            url="https://notpx.app",
            platform="android",
        )
    print(app_url)


    print(4)
    pa = notpixel_actions.PixelActions(
        app_url,
        proxy_host=proxy_host,
        proxy_port=6200,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
    )
    print(5)
    task = (
        (80, 80, (255, 141, 161)),
        (80, 81, (255, 141, 161)),
        (81, 80, (255, 141, 161)),
        (81, 81, (255, 141, 161)),
    )
    pa.gui_app_start()
    code.interact(local=locals())
    job_result = pa.run(task)
    print(6)
    print(job_result)
    # balance = pa.draw()
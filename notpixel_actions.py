import asyncio
import io
import json
import logging
import random
import re
import time
from hashlib import md5
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image

import notpixel_tools
from centrifucka import Fucka
import secure_browser
import settings
import useragents
import utils

HTTP_REQUEST_TIMEOUT = 30


class PixelActions:
    def __init__(
        self,
        web_app_entry_url,
        proxy_host="",
        proxy_port=0,
        proxy_user="",
        proxy_password="",
        proxy_extention_path="",
        gui_browser_worker_type=None,  # chrome or firefox, allow NONE to not start the browser
        headless=False,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logging_name="PixelActions unnamed",
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

        self.web_app_entry_url = web_app_entry_url
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port) if proxy_port is not None else 0
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.proxy_extention_path = proxy_extention_path

        self.pool = ThreadPoolExecutor(max_workers=2)
        self.centrifuga = Fucka(
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_password=self.proxy_password,
            logfile_path=logfile_path,
            logging_level=logging_level,
            logging_name=logging_name,
        )

        self.energy = 0
        self.auth_token = self.get_autorization_header()
        self.init_user_agent()

        # self.requests_proxy = None
        # if proxy_host:
        #     self.requests_proxy = {
        #         "http": f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
        #         "https": f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
        #     }
        self.proxy_string = None
        if proxy_host:
            self.proxy_string = (
                f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
            )

        self.sb = None
        if gui_browser_worker_type:
            self.gui_init_browser(gui_browser_worker_type, headless)

    def gui_init_browser(self, gui_browser_worker_type="chrome", headless=False):
        browser_args = {
            "proxy_host": self.proxy_host,
            "proxy_port": self.proxy_port,
            "proxy_user": self.proxy_user,
            "proxy_password": self.proxy_password,
            "headless": headless,
        }
        if self.proxy_extention_path:
            browser_args["extention_path"] = self.proxy_extention_path
        if gui_browser_worker_type == "firefox":
            self.sb = secure_browser.SecFirefoxBrowser(**browser_args)
        elif gui_browser_worker_type == "chrome":
            self.sb = secure_browser.SecChromeBrowser(**browser_args)

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

    def gui_app_start(self, retries=None, timeout=5):
        if retries:
            for i in range(retries):
                self.sb.browser.get(self.web_app_entry_url)
                try:
                    WebDriverWait(self.sb.browser, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, "//div/button"))
                    )
                    break
                except BaseException as e:
                    print(f"not found button: {e}")
        else:
            self.sb.browser.get(self.web_app_entry_url)

    def init_user_agent(self):
        dec_url = unquote(unquote(self.web_app_entry_url))
        user_id_match = re.search(r'id":(\d+),', dec_url)
        if not user_id_match:
            user_id = random.randint(0, 100)
        else:
            user_id = user_id_match.group(1)
        l = len(useragents.mobile)
        self.user_agent = useragents.mobile[int(user_id) % l]["ua"]

    def get_autorization_header(self):
        q, w = self.web_app_entry_url.split("#tgWebAppData=")
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
            "User-Agent": self.user_agent,  # "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36",
            "Referer": "https://app.notpx.app/",
            "Priority": "u=1, i",
            "Origin": "https://app.notpx.app",
        }

    async def sleep_after_request(self, sleep_min=14, sleep_max=18):
        await asyncio.sleep(random.randint(100 * sleep_min, 100 * sleep_max) / 100)

    async def emulate_js_loading(self, mainpage_content):
        self.logger.info(f"Start Emulate JS loading")
        headers = {"User-Agent": self.user_agent}
        content = mainpage_content.decode()
        js_hrefs = re.findall(r'href="(.+?\.js)"', content)
        loaded_js_count = 0
        bad_loaded_js_count = 0
        results = await asyncio.gather(
            *[
                notpixel_tools.http_request(
                    "GET",
                    "https://app.notpx.app" + js_href,
                    headers,
                    proxy=self.proxy_string,
                    http_timeout=HTTP_REQUEST_TIMEOUT,
                    good_statuses=[200],
                    logger=self.logger,
                )
                for js_href in js_hrefs
            ]
        )
        for i in results:
            status = i.get("status")
            if status == 200:
                loaded_js_count += 1
            else:
                bad_loaded_js_count += 1
        self.logger.info(
            f"Emulate JS loading GOOD: {loaded_js_count}, BAD: {bad_loaded_js_count}"
        )
        pass

    async def get_ws_token(self):
        self.logger.debug(f"Start get websocket token")
        headers = self.get_headers_api()
        url = "https://notpx.app/api/v1/users/me"
        result = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        data = json.loads(result["content"])
        token = data.get("websocketToken")
        self.logger.debug(f"Got ws token: {token}")
        return token

    async def emulate_app_start(self):
        self.logger.debug(f"Start GET entry URL")
        headers = {"User-Agent": self.user_agent}
        result = await notpixel_tools.http_request(
            "GET",
            self.web_app_entry_url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        await self.emulate_js_loading(result.get("content", ""))
        await self.sleep_after_request()
        status = result.get("status")
        content_len = len(result.get("content"))
        self.logger.info(
            f"Finish GET entry URL GET, status: {status}, content len: {content_len}"
        )

    async def claim(self):
        url = "https://notpx.app/api/v1/mining/claim"
        self.logger.debug(f"Start CLAIM")
        if self.sb:
            browser_url = "https://app.notpx.app/claiming"
            if self.sb.browser.current_url != browser_url:
                self.sb.browser.get(browser_url)
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 500, 504],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        content = result.get("content")
        content_len = len(content)
        self.logger.info(
            f"Finish CLAIM, status: {status}, content: {content} content len: {content_len}"
        )

    async def upgrade_boost(self, key):
        url = f"https://notpx.app/api/v1/mining/boost/check/{key}"
        self.logger.debug(f"Start UPGRADE {key}")
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        content = result.get("content")
        content_len = len(content)
        self.logger.info(
            f"Finish UPGRADE {key}, status: {status}, content: {content} content len: {content_len}"
        )

    async def install_upgrades(self, balance, boosts):

        # ordered by upgrade priority
        upgrade_keys = {
            "reChargeSpeed": settings.upgrade_charge_restoration_price,
            "paintReward": settings.upgrade_repaint_price,
            "energyLimit": settings.upgrade_charge_count,
        }
        for uk in upgrade_keys:
            current_level = boosts.get(uk)
            upgrade_price = upgrade_keys[uk].get(current_level + 1)
            if balance > upgrade_price:
                try:
                    await self.upgrade_boost(uk)
                except:
                    self.logger.error(f"Upgrade {uk} failed")
                balance -= upgrade_price

    async def get_templates(self):
        get_from_page = 2
        for i in range(get_from_page):
            url = f"https://notpx.app/api/v1/image/template/list?limit=12&offset={get_from_page * i}"
            self.logger.debug(f"Start GET template list from page {i}")
            headers = self.get_headers_api()
            result = await notpixel_tools.http_request(
                "GET",
                url,
                headers,
                proxy=self.proxy_string,
                http_timeout=HTTP_REQUEST_TIMEOUT,
                good_statuses=[200],
                logger=self.logger,
            )
            await self.sleep_after_request()
        content = result.get("content")
        data = json.loads(content)
        templates = {}
        for ti in data:
            _id = ti.get("templateId")
            url = ti.get("url")
            templates[_id] = url
        self.logger.info(f"GOT template list: {templates.keys()}")
        return templates

    async def get_template_pixels_by_url(self, template_image_url: str):
        self.logger.debug(f"Start GET template image info {template_image_url}")
        headers = {"User-Agent": self.user_agent}
        image_info = await notpixel_tools.http_request(
            "GET",
            template_image_url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        image_content = image_info.get("content")
        pixels = await asyncio.get_event_loop().run_in_executor(
            self.pool, notpixel_tools.get_pixels, image_content
        )
        return pixels

    async def get_template_colors(self, template_id: int):
        url = f"https://notpx.app/api/v1/image/template/{template_id}"
        self.logger.debug(f"Start GET template info {template_id}")
        headers = self.get_headers_api()
        template_info = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        content = template_info.get("content")
        template_info_d = json.loads(content)
        color_data = {}
        image_url = template_info_d.get("url")
        if image_url:
            pixels = await self.get_template_pixels_by_url(image_url)
            image_size = template_info_d.get("imageSize")
            for x in range(image_size):
                for y in range(image_size):
                    pixel = pixels[x, y]
                    pixel_id = (
                        (template_info_d.get("y") + y) * 1000
                        + template_info_d.get("x")
                        + x
                        + 1
                    )
                    color = notpixel_tools.rgb_to_hex(pixel[:3])
                    color_data[pixel_id] = color

        else:
            self.logger.error(f"Failed to get image pixels info {image_url}")

        self.logger.info(f"Got template info {template_info_d}")

        return color_data

    async def select_template(self, template_id):
        url = f"https://notpx.app/api/v1/image/template/subscribe/{template_id}"
        self.logger.debug(f"Start Choose template {template_id}")
        headers = self.get_headers_api()
        template_info = await notpixel_tools.http_request(
            "PUT",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 204, 403],
            logger=self.logger,
        )
        status = template_info.get("status")
        if status == 403:
            self.logger.info(f"Template {template_id} was selected before. ITS BAD")
        elif status in [200, 204]:
            self.logger.info(f"Template {template_id} selected successfully")

    async def get_account_state(self, claim=True, upgrade=True):
        url = "https://notpx.app/api/v1/mining/status"
        self.logger.debug(f"Start GET account status")
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        content = result.get("content")
        content_len = len(content)
        self.logger.info(
            f"Finish GET account state, status: {status}, content: {content} content len: {content_len}"
        )

        data = json.loads(content)
        charges = data.get("charges")
        recharge_speed = data.get("reChargeSpeed", 0) / 1000  # in sec
        max_charges = data.get("maxCharges", 0)
        balance = data.get("userBalance")

        claimed = data.get("claimed")
        if claim and claimed == 0:
            try:
                await self.claim()
            except:
                self.logger.error("Claim failed")
        boosts = data.get("boosts", {})
        if upgrade and boosts:
            await self.install_upgrades(balance=balance, boosts=boosts)

        return {
            "charges": charges,
            "charge_restore_speed": recharge_speed,
            "max_charges": max_charges,
            "balance": balance,
        }

    async def paint_pixel_old(self, x: int, y: int, color: tuple):
        if self.sb:
            browser_url = "https://app.notpx.app/"
            if self.sb.browser.current_url != browser_url:
                self.sb.browser.get(browser_url)
        url = "https://notpx.app/api/v1/repaint/start"
        color_s = "#" + notpixel_tools.rgb_to_hex(color)
        self.logger.debug(f"Start PAINT PIXEL {x}:{y}")
        headers = self.get_headers_api()
        pixel_id = y * 1000 + x + 1
        result = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            json_p={"pixelId": pixel_id, "newColor": color_s},
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        content = result.get("content")
        content_len = len(content)
        self.logger.info(
            f"Finish PAINT PIXEL {x}:{y} to {color_s}, status: {status}, content: {content} content len: {content_len}"
        )

    async def paint_pixel(self, pixel_id: int, color: str):
        url = "https://notpx.app/api/v1/repaint/start"
        if not color.startswith("#"):
            color = f"#{color}"
        self.logger.debug(f"Start PAINT PIXEL {pixel_id} to {color}")
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            json_p={"pixelId": pixel_id, "newColor": color},
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200],
            logger=self.logger,
        )
        status = result.get("status")
        content = result.get("content")
        content_len = len(content)
        self.logger.info(
            f"Finish PAINT PIXEL {pixel_id} to {color}, status: {status}, content: {content} content len: {content_len}"
        )
        return status == 200

    async def paint(self, pixels_to_paint):
        painted = []
        for x, y, task_pix_color in pixels_to_paint:
            await self.paint_pixel_old(x, y, task_pix_color)
            painted.append((x, y))
            self.energy -= 1
            if self.energy < 1:
                return painted
        return painted

    async def paint_pixels(self, pixels_to_paint):
        if self.sb:  # NOT ASYNC
            self.gui_app_start()
            self.gui_click_initial_buttons()
        else:
            await self.emulate_app_start()

        acc_state = await self.get_account_state()

        self.energy = acc_state.get("charges", 0)
        recharge_speed = acc_state.get("charge_restore_speed", 0)
        max_charges = acc_state.get("max_charges", 0)

        painted = await self.paint(pixels_to_paint)

        job_status = {
            "painted": painted,
            "charges": self.energy,
            "energy_restore_speed": recharge_speed,
            "max_energy": max_charges,
        }

        self.logger.info(f"Job done, result: {job_status}")

        return job_status

    async def repaint_pixels(self):
        await self.emulate_app_start()
        ws_token = await self.get_ws_token()
        acc_state = await self.get_account_state(claim=True, upgrade=True)
        # charges = acc_state.get("charges", 0)
        charges = 3
        templates = await self.get_templates()

        template_id = random.choice(list(templates))
        await self.select_template(template_id=template_id)
        good_pixel_colors = await self.get_template_colors(template_id)
        await self.centrifuga.init_client(token=ws_token, user_agent=self.user_agent)
        paint_task = await self.centrifuga.collect_pixels_to_repaint(
            charges, good_pixels=good_pixel_colors
        )

        # repaint
        for shot_i in range(charges):
            pixel_id = random.choice(list(paint_task.keys()))
            color = paint_task.pop(pixel_id)
            try:
                await self.paint_pixel(pixel_id, color)
                charges -= 1
            except BaseException as e:
                logging.error((f"FAILED PAINT PIXEL {pixel_id} to {color}"))

        # update acc state (not nessesary)
        try:
            acc_state = await self.get_account_state(claim=False, upgrade=False)
            charges = acc_state.get("charges", 0)
        except:
            logging.error(
                "Error updating acc state after actions. Return initial values"
            )
            acc_state["charges"] = charges

        # {
        #     "charges": charges,
        #     "charge_restore_speed": recharge_speed,
        #     "max_charges": max_charges,
        #     "balance": balance,
        # }
        return acc_state

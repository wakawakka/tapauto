import asyncio
import datetime
import io
import json
import logging
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from urllib.parse import unquote
import os

import pandas as pd
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import notpixel_tools
import secure_browser
import settings
import useragents
import utils
from centrifucka import Fucka
import dbutils

HTTP_REQUEST_TIMEOUT = 30
TEMPLATE_PAGE = 4

PIRATE_HAT_TEMPLATE_ID = "6444194100"
TEMPLATE_X = 160
TEMPLATE_Y = 480
TEMPLATE_SIZE = 32


class PixelActions:
    def __init__(
        self,
        web_app_entry_url: str,
        session_id: str,
        db: dbutils.TDB,
        worker_start_datetime: datetime.datetime,
        proxy_host="",
        proxy_port=0,
        proxy_user="",
        proxy_password="",
        proxy_extention_path="",
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logging_name="PixelActions unnamed",
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

        self.worker_start_datetime = worker_start_datetime

        self.web_app_entry_url = web_app_entry_url
        self.db = db
        self.session_id = session_id
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port) if proxy_port is not None else 0
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.proxy_extention_path = proxy_extention_path

        # self.allowed_tasks = {i: False for i in settings.free_tasks}
        self.allowed_tasks = {i: True for i in settings.free_tasks}

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

        self.proxy_string = None
        if proxy_host:
            self.proxy_string = (
                f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
            )

        self.sb = None

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

    async def load_index(self, index_href):
        # for check in settings.tasks_check_rules:
        self.logger.info(f"Start Emulate JS index loading")
        headers = {"User-Agent": self.user_agent}

        index_last_update = self.worker_start_datetime
        dt_rfc_format = index_last_update.strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers["If-Modified-Since"] = dt_rfc_format
        # index_last_update = await self.db.get_user_index_update_time(self.session_id)
        # dt_rfc_format = None
        # if index_last_update:
        #     dt_last_update = datetime.datetime.fromisoformat(index_last_update)
        #     dt_rfc_format = dt_last_update.strftime("%a, %d %b %Y %H:%M:%S GMT")
        #     headers["If-Modified-Since"] = dt_rfc_format

        index_request = await notpixel_tools.http_request(
            "GET",
            "https://app.notpx.app" + index_href,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 304],
            logger=self.logger,
        )
        status = index_request.get("status")
        content = index_request.get("content")

        self.logger.info(
            f"JS {index_href} loading status: {status}. Size: {len(content)}"
        )

        if status == 200:
            logger = utils.get_logger(
                filepath="contoller.log",
                level=logging.DEBUG,
                name=f"pixel:{self.session_id}",
            )
            if settings.FAIL_ON_JS_CHANGE:
                error_message = (
                    "INDEX PAGE UPDATED FROM START OF THE WORKER. PIXEL TASKS START BANNED."
                )
                logger.error(error_message)
                settings.EXECUTION_BAN_TASKS.add(settings.PIXEL_TASK_NAME)
                raise Exception(error_message)

        # if status == 200:
        #     dt_now = datetime.datetime.now(datetime.UTC)
        #     dt_now_rfc = dt_now.strftime("%a, %d %b %Y %H:%M:%S GMT")
        #     self.logger.info(
        #         f"Index page downloaded. Setting index download time {dt_now_rfc} on user {self.session_id}"
        #     )
        #     await self.db.set_user_index_update_time(self.session_id, dt_now)

        #     for task in settings.free_tasks:
        #         task_check = settings.free_tasks[task]
        #         if not task_check in content:
        #             self.logger.info(
        #                 f"Check of {task_check} in index failed. Task {task} completion blocked."
        #             )
        #             self.allowed_tasks[task] = False
        #         else:
        #             self.logger.info(
        #                 f"Check of {task_check} in index Success. Task {task} completion allowed."
        #             )
        #             self.allowed_tasks[task] = True
        # elif status == 304:
        #     self.logger.info(
        #         f"All task completion blocked until new index.js download. Last load was {dt_rfc_format}"
        #     )

    async def emulate_js_loading(self, mainpage_content):
        self.logger.info(f"Start Emulate JS loading")

        dt_now = datetime.datetime.now(datetime.UTC)
        dt_since = dt_now - datetime.timedelta(minutes=30)
        time_since = dt_since.strftime("%a, %d %b %Y %H:%M:%S GMT")

        headers = {"User-Agent": self.user_agent, "If-Modified-Since": time_since}
        content = mainpage_content.decode()

        index_href_match = re.search(r'module.+?src="(.+?index-.+?\.js)"', content)
        js_hrefs = re.findall(r'modulepreload.+?href="(.+?\.js)"', content)

        if index_href_match:
            index_href = index_href_match.group(1)
            await self.load_index(index_href)
        else:
            raise Exception(
                "Index.js not found. Update the code. (function: emulate_js_loading)"
            )

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
                    good_statuses=[200, 304],
                    logger=self.logger,
                    retry_count=1,
                )
                for js_href in js_hrefs
            ]
        )
        sum_len = 0
        for i in results:
            status = i.get("status")
            content = i.get("content")
            sum_len += len(content)
            if status in [200, 304]:
                loaded_js_count += 1
            else:
                bad_loaded_js_count += 1
        self.logger.info(
            f"Emulate JS loading GOOD: {loaded_js_count}, BAD: {bad_loaded_js_count} SIZE: {sum_len} bytes."
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
        if settings.DOWNLOAD_JS_SCRIPTS:
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
            if upgrade_price and balance > upgrade_price:
                try:
                    await self.upgrade_boost(uk)
                except:
                    self.logger.error(f"Upgrade {uk} failed")
                balance -= upgrade_price

    async def get_templates(self, get_from_page):
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

    async def get_template_pixels_by_url(self, template_id, template_image_url: str):
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
        template_content_path = os.path.join(
            settings.templates_dir, f"{template_id}.png"
        )
        with open(template_content_path, "wb") as f:
            f.write(image_content)

        self.logger.info(
            f"Downloaded template {template_image_url}. SIZE: {len(image_content)}"
        )
        pixels = await asyncio.get_event_loop().run_in_executor(
            self.pool, notpixel_tools.get_pixels, image_content
        )
        return pixels

    async def get_my_template(self):
        url = f"https://notpx.app/api/v1/image/template/my"
        self.logger.debug(f"Start GET my template info")
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
        self.logger.info(f"My template info: {data}")
        return data

    async def get_my_tournament_template(self):
        url = f"https://notpx.app/api/v1/tournament/template/subscribe/my"
        self.logger.debug(f"Start GET my template info")
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "GET",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 404],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        if status == 404:
            return
        else:
            content = result.get("content")
            data = json.loads(content)
            self.logger.info(f"My template info: {data}")
            return data

    async def select_tournament_template(self, template_id):
        url = f"https://notpx.app/api/v1/tournament/template/subscribe/{template_id}"
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

    async def get_my_template_good_pixels(self, my_template_info):
        template_id = my_template_info.get("id")
        template_url = my_template_info.get("url")

        template_info_path = os.path.join(settings.templates_dir, f"{template_id}.json")
        with open(template_info_path, "w") as f:
            f.write(json.dumps(my_template_info, indent=4))

        good_pixel_colors = None
        good_pixel_colors = await self.get_template_colors_from_cache(template_id)
        if not good_pixel_colors:
            pixels = await self.get_template_pixels_by_url(template_id, template_url)
            good_pixel_colors = await self.pixels_to_color_data(
                pixels=pixels, template_info=my_template_info
            )
        return good_pixel_colors

    async def get_template_pixels_from_cache(self, template_id):
        try:
            template_image_path = os.path.join(
                settings.templates_dir, f"{template_id}.png"
            )
            with open(template_image_path, "rb") as f:
                image_content = f.read()

            pixels = await asyncio.get_event_loop().run_in_executor(
                self.pool, notpixel_tools.get_pixels, image_content
            )
            return pixels
        except:
            return None

    async def get_template_info_from_cache(self, template_id):
        try:
            template_info_path = os.path.join(
                settings.templates_dir, f"{template_id}.json"
            )
            with open(template_info_path, "r") as f:
                template_info_content = f.read()
                template_info = json.loads(template_info_content)
                return template_info
        except:
            return None

    async def pixels_to_color_data(self, pixels, template_info: dict):
        color_data = {}
        image_size = template_info.get("size")
        for x in range(image_size):
            for y in range(image_size):
                pixel = pixels[x, y]
                pixel_id = (
                    (template_info.get("y") + y) * 1000 + template_info.get("x") + x + 1
                )
                color = notpixel_tools.rgb_to_hex(pixel[:3])
                color_data[pixel_id] = color
        return color_data

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
        template_info_path = os.path.join(settings.templates_dir, f"{template_id}.json")
        with open(template_info_path, "w") as f:
            f.write(json.dumps(template_info_d, indent=4))

        image_url = template_info_d.get("url")

        color_data = {}
        if image_url:
            pixels = await self.get_template_pixels_by_url(template_id, image_url)
            color_data = await self.pixels_to_color_data(
                pixels=pixels, template_info=template_info_d
            )

        else:
            self.logger.error(f"Failed to get image pixels info {image_url}")

        self.logger.info(f"Got template info {template_info_d}")

        return color_data

    async def get_template_colors_from_cache(self, template_id):
        pixels = await self.get_template_pixels_from_cache(template_id=template_id)
        template_info = await self.get_template_info_from_cache(template_id=template_id)
        if pixels and template_info:
            self.logger.debug(
                f"Found cache instance of {template_id}. Using it without download."
            )
            color_data = await self.pixels_to_color_data(
                pixels=pixels, template_info=template_info
            )
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

    async def complete_tasks(self, tasks):
        for task_name in self.allowed_tasks:
            task_completed = tasks.get(task_name)
            if task_completed or not self.allowed_tasks[task_name]:
                continue
            self.logger.info(f"Found uncompleted task: {task_name}")
            url = f"https://notpx.app/api/v1/mining/task/check/{task_name}"
            headers = self.get_headers_api()
            complete_task_info = await notpixel_tools.http_request(
                "GET",
                url,
                headers,
                proxy=self.proxy_string,
                http_timeout=HTTP_REQUEST_TIMEOUT,
                good_statuses=[200],
                logger=self.logger,
            )
            self.logger.info(f"Task complete result: {complete_task_info}")

    async def get_account_state(self, claim=False, upgrade=False, complete_tasks=False):
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

        tasks = data.get("tasks")
        if complete_tasks:
            await self.complete_tasks(tasks)

        return {
            "charges": charges,
            "charge_restore_speed": recharge_speed,
            "max_charges": max_charges,
            "balance": balance,
        }

    async def enter_secret_word(self, word: str):
        url = "https://notpx.app/api/v1/mining/quest/check/secretWord"
        self.logger.debug(f'Start send secret word "{word}"')
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            json_p={"secret_word": word},
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 403],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = result.get("status")
        content = result.get("content")
        if content:
            content = content.decode()
        await self.db.add_notpixel_secret_try(
            number=self.session_id, word=word, responce=content
        )
        self.logger.info(f"Finish send secret word {word}, answer: {content}")

    async def offer_check(self):
        url = "https://notpx.app/api/v1/offer/check"
        self.logger.debug(f"Start Offer check")
        headers = self.get_headers_api()
        result = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 404],
            logger=self.logger,
        )
        status = result.get("status")
        content = result.get("content")
        self.logger.info(f"Finish Offer check. Status: {status}, Content: {content}.")

    async def periods_check(self):
        url = "https://notpx.app/api/v1/tournament/periods"
        self.logger.debug(f"Start periods check")
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
        status = result.get("status")
        content = result.get("content")
        self.logger.info(f"Finish periods check. Status: {status}, Content: {content}.")

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

    async def repaint_pixels(self):
        await self.emulate_app_start()
        ws_token = await self.get_ws_token()
        await self.centrifuga.init_client(token=ws_token, user_agent=self.user_agent)

        acc_state = await self.get_account_state(
            claim=True, upgrade=True, complete_tasks=False
        )
        # acc_state = await self.get_account_state(
        #     claim=False, upgrade=False, complete_tasks=False
        # )
        # offer_check = await self.offer_check()
        periods_check = await self.periods_check()
        charges = acc_state.get("charges", 0)
        # if charges > 12:
        #     charges = 12
        # charges = 1

        good_pixel_colors = None
        my_tournament_template = await self.get_my_tournament_template()

        if not settings.SUCKER:
            if settings.KAKER:
                self.logger.info('KAKER')
                paint_task = await notpixel_tools.get_job(Image.open(settings.KAKER_IMG), settings.KAKER_LOCATION)
                for shot_i in range(charges):
                    pixel_id = random.choice(list(paint_task.keys()))
                    color = paint_task.pop(pixel_id)
                    try:
                        await self.paint_pixel(pixel_id, color)
                        charges -= 1
                    except BaseException as e:
                        self.logger.error((f"FAILED PAINT PIXEL {pixel_id} to {color}"))
            else:
                if my_tournament_template:
                    good_pixel_colors = await self.get_my_template_good_pixels(
                        my_tournament_template
                    )
                else:
                    await self.select_template(PIRATE_HAT_TEMPLATE_ID)
                    my_tournament_template = await self.get_my_tournament_template()
                    await self.sleep_after_request(5, 10)
                    good_pixel_colors = await self.get_my_template_good_pixels(
                        my_tournament_template
                    )

                if good_pixel_colors:
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
                            self.logger.error((f"FAILED PAINT PIXEL {pixel_id} to {color}"))

                    # try:
                    #     old_secrets = await self.db.get_notpixel_secret_tries(self.session_id)
                    #     for word in settings.secret_words:
                    #         if word not in old_secrets:
                    #             await self.enter_secret_word(word)
                    # except BaseException as e:
                    #     self.logger.error(f"Failed to send secret word. {e}")

                    # update acc state (not nessesary)
                else:
                    self.logger.error(
                        f"Not good pixel colors detected. NOPAINT: {settings.NOPAINT}"
                    )
        else:
            await self.centrifuga.emulate_centrifuga_connect()
            for i in range(charges):
                x_pad = random.randint(0, 32)
                y_pad = random.randint(0, 32)
                colors = ["#FF3881", "#7EED56", "#6D001A"]
                pixel_id = (TEMPLATE_Y + y_pad) * 1000 + TEMPLATE_X + x_pad + 1
                await self.paint_pixel(pixel_id, random.choice(colors))
                charges -= 1

                pass

        try:
            acc_state = await self.get_account_state(
                claim=False, upgrade=False, complete_tasks=False
            )
            charges = acc_state.get("charges", 0)
        except:
            self.logger.error(
                "Error updating acc state after actions. Return initial values"
            )
            acc_state["charges"] = charges

        return acc_state

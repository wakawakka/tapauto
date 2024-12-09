import asyncio
import datetime
import io
import json
import logging
import random
import re
import time
from urllib.parse import unquote
import os
import string
import base64
import binascii

import notpixel_tools
import secure_browser
import settings
import useragents
import utils
import dbutils

# TODO
# check fix upgrade BUG
# add TAP robot perchase
#

HTTP_REQUEST_TIMEOUT = 30

X_APP = "tapswap_server"
X_CV = "662"
X_TOUCH = "1"

mission_codes = {
    "M2479": "sick",
    "M2480": "edur",
    "M2488": "g8wqa",
    "M2489": "l4le1t",
    "M2490": "k9swd",
    "M2491": "wuhi9t",
    "M2492": "hw7qp",
    "M2493": "4rte2i",
    "M2494": "bl2e1",
    "M2495": "elis6t",
    "M2496": "h2it5",
    "M2497": "54z1s",
    "M2498": "r9es5",
    "M2499": "wieb",
    "M2500": "86ne",
    "M2501": "n4c3",
    "M2502": "3u8m",
    "M2503": "blya",
    "M2504": "t83a",
    "M2505": "95iv",
    "M2506": "2m34",
    "M2507": "btfo",
    "M2508": "e9mb",
    "M2509": "kise",
    "M2510": "ca1t",
    "M2511": "n2g7",
    "M2518": "aabily",
    "M2519": "9iner",
    "M2520": "ps2ct",
    "M2521": "accoy",
    "M2522": "9va5",
    "M2523": "grad",
    "M2524": "morn",
    "M2525": "alte",
    "M2526": "l8e6",
    "M2527": "gipn",
    "M2528": "ebri",
    "M2529": "96al",
    "M2530": "i1ze",
    "M1325": "UPD9&",
    "M1326": "8opiq",
    "M1327": "7khUy",
    "M1328": "Q3#PM",
    "M1329": "MAS%3",
    "M1330": "G)*5B",
    "M1331": "3$#Wq",
    "M1332": "2W%fR",
    "M1333": "5KiOu",
    "M1334": "m*T%7",
    "M1337": "CB6t$",
    "M1338": ")7fsq",
    "M1339": "6tue",
    "M1340": "1NpY6",
    "M1341": "V&6?9",
    "M2531": "vmre",
    "M2532": "d2r2",
    "M2533": "kite",
    "M2534": "6ne9",
    "M2535": "g2pu",
    "M2536": "kawa",
    "M2537": "atif",
    "M2538": "must",
    "M2539": "krwi",
    "M2540": "2rp5",
    "M2541": "anaj",
    "M2542": "efir",
    "M2543": "i3me",
    "M2544": "fabe",
    "M2545": "4l88",
    "M2546": "pivo",
    "M1342": "m8L?H",
    "M1343": "JP09K",
    "M1344": "%2BRe",
    "M1345": "9OPyf",
    "M1346": "8AQ@g",
    "M1347": "5F0Lm",
    "M1348": "5KpTR",
    "M1349": "1CV&1",
    "M1350": "3T&?W",
    "M1351": "3K%pg",
    "M1352": "3WQ@#",
    "M1353": "N1%rE",
    "M2547": "qurt",
    "M2548": "a4l7",
    "M2549": "pedr",
    "M2550": "3e9s",
    "M2551": "r8e5",
    "M2552": "uprt",
    "M2553": "wial",
    "M2554": "purp",
    "M2555": "4s6h",
    "M2556": "pves",
    "M2557": "resh",
    "M2558": "92en",
    "M2559": "Oi7*A",
    "M1354": "P&dE4",
}


class TapswapActions:
    def __init__(
        self,
        web_app_entry_url: str,
        telegram_user_id,
        telegram_session_id,
        selen,
        db: dbutils.TDB,
        worker_start_datetime: datetime.datetime,
        proxy_host="",
        proxy_port=0,
        proxy_user="",
        proxy_password="",
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logging_name="TapswapActions unnamed",
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )
        self.worker_start_datetime = worker_start_datetime

        self.web_app_entry_url = web_app_entry_url
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port) if proxy_port is not None else 0
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        self.proxy_string = None
        if proxy_host:
            self.proxy_string = (
                f"socks5://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
            )
        self.selen = selen
        self.db = db
        self.telegram_user_id = telegram_user_id
        self.telegram_session_id = telegram_session_id

        self.init_user_agent()

    async def sleep_after_request(self, sleep_min=10, sleep_max=18):
        sleep_time = random.randint(100 * sleep_min, 100 * sleep_max) / 100
        self.logger.debug(f"Go sleep for {sleep_time}")
        await asyncio.sleep(sleep_time)

    def init_user_agent(self):
        dec_url = unquote(unquote(self.web_app_entry_url))
        user_id_match = re.search(r'id":(\d+),', dec_url)
        if not user_id_match:
            user_id = random.randint(0, 100)
        else:
            user_id = user_id_match.group(1)
        l = len(useragents.mobile)
        self.user_agent = useragents.mobile[int(user_id) % l]["ua"]

    def dt_convert_header(self, dt: datetime.datetime):
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def get_base_headers(
        self,
        origin: str = None,
        referer: str = None,
        not_modified_since: datetime.datetime = None,
    ):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.9;q=0.9",
            "Sec-Fetch-Dest": "empty",
            "sec-fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.user_agent,  # "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36",
            "Priority": "u=1, i",
        }
        if not_modified_since:
            headers["If-Modified-Since"] = self.dt_convert_header(not_modified_since)
        if referer:
            headers["Referer"] = referer
        if origin:
            headers["Origin"] = origin
        return headers

    def get_api_headers(self, bearer=False):
        headers = self.get_base_headers(
            origin="https://app.tapswap.club", referer="https://app.tapswap.club/"
        )
        headers["Accept"] = "*/*"
        headers["x-app"] = X_APP
        headers["x-touch"] = X_TOUCH
        headers["x-cv"] = X_CV
        headers["Content-Type"] = "application/json"
        if bearer:
            headers["Authorization"] = f"Bearer {self.bearer}"
            headers["Cache-Id"] = self.cache_id
        return headers

    async def load_index(self, index_href):
        # for check in settings.tasks_check_rules:
        self.logger.info(f"Start Emulate JS index loading")
        headers = {"User-Agent": self.user_agent}

        # index_last_update = self.worker_start_datetime
        # dt_rfc_format = index_last_update.strftime("%a, %d %b %Y %H:%M:%S GMT")
        # headers["If-Modified-Since"] = dt_rfc_format
        # index_last_update = await self.db.get_user_index_update_time(self.session_id)
        # dt_rfc_format = None
        # if index_last_update:
        #     dt_last_update = datetime.datetime.fromisoformat(index_last_update)
        #     dt_rfc_format = dt_last_update.strftime("%a, %d %b %Y %H:%M:%S GMT")
        #     headers["If-Modified-Since"] = dt_rfc_format
        index_request = await notpixel_tools.http_request(
            "GET",
            "https://app.tapswap.club" + index_href,
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

        if f'this.api.headers.set("x-cv","{X_CV}")'.encode() not in content:
            logger = utils.get_logger(
                filepath="contoller.log",
                level=logging.DEBUG,
                name=f"tapswap:{self.telegram_session_id}",
            )
            error_message = "BUILD NUMBER CHANGED. TAPSWAP TASKS START BANNED."
            logger.error(error_message)
            settings.EXECUTION_BAN_TASKS.add(settings.TAPSWAP_TASK_NAME)
            raise Exception(error_message)
        else:
            self.logger.info("Build number check passed")

    async def load_main_page(self):
        headers = self.get_base_headers()
        request = await notpixel_tools.http_request(
            "GET",
            self.web_app_entry_url,
            headers,
            proxy=self.proxy_string,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 304],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content").decode()
        self.logger.debug(f"GET main page status: {status}. Len: {len(content)}")

        index_href_match = re.search(r'module.+?src="(.+?main-.+?\.js)"', content)

        if index_href_match:
            index_href = index_href_match.group(1)
            await self.load_index(index_href)
        else:
            raise Exception(
                "main.js not found. Update the code. (function: load_main_page)"
            )

    def get_autorization_header(self):
        q, w = self.web_app_entry_url.split("#tgWebAppData=")
        a, s = w.split("&", 1)
        return unquote(a)

    async def login(self, bot_key: str = "app_bot_0", referrer: str = ""):
        url = "https://api.tapswap.club/api/account/login"
        headers = self.get_api_headers(bearer=False)
        auth_header = self.get_autorization_header()
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p={
                "bot_key": bot_key,
                "init_data": auth_header,
                "referrer": referrer,
            },
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.debug(
            f"POST LOGIN page status: {status}. Content len: {len(content)}"
        )
        data = json.loads(content)
        return data.get("chq")

    def solve_challenge(self, encoded_chq):
        # magic_number = 232
        key = 157

        chq_bytes = binascii.unhexlify(encoded_chq)
        original_js = "".join([chr(i ^ key) for i in chq_bytes])

        self.logger.info(f"Original decoded chq challenge js len: {len(original_js)}")
        js = (
            "var cache_id = ''; "
            + "window.ctx = {api: {setHeaders : function(t){for(const[i,n]of Object.entries(t))cache_id = n}}};"
            + "window.ctx.api.headers = {get: function(a){return "
            + f"{X_CV}"
            + ";}};"
            + "Telegram = {WebApp: {initDataUnsafe: {user: {id:"
            + f"{self.telegram_user_id}"
            + "}}}};"
            + original_js
        )
        html_path = "assets/tapswap.html"
        nix_abspath = os.path.abspath(html_path).replace("\\", "/")
        self.logger.debug("Start selenium challenge get")
        self.selen.browser.get(f"file:///{nix_abspath}")
        self.logger.debug("Finish selenium challenge get")
        js_base64_encoded = base64.b64encode(js.encode()).decode()

        script = (
            f'jsb64="{js_base64_encoded}"; x = eval(atob(jsb64)); return [x,cache_id];'
        )
        self.logger.debug("Start selenium challenge script execute")
        ret = self.selen.browser.execute_script(script)
        self.logger.debug("Finish selenium challenge script execute")
        answer, cache_id = ret
        # answer += magic_number
        return {"chq": answer, "cache_id": cache_id}

    async def challenge(
        self, bot_key: str = "app_bot_0", referrer: str = "", chq_challenge={}
    ):
        url = "https://api.tapswap.club/api/account/challenge"
        headers = self.get_api_headers(bearer=False)

        headers["Cache-Id"] = chq_challenge.get("cache_id")
        auth_header = self.get_autorization_header()
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p={
                "bot_key": bot_key,
                "chr": chq_challenge.get("chq"),
                "init_data": auth_header,
                "referrer": referrer,
            },
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201, 400],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")

        self.logger.info(
            f"POST Challenge page status: {status}. Content len: {len(content)}."
        )
        if status == 400:
            logger = utils.get_logger(
                filepath="contoller.log",
                level=logging.DEBUG,
                name=f"tapswap:{self.telegram_session_id}",
            )
            error_message = "Challange status: 400. TAPSWAP TASKS START BANNED."
            logger.error(error_message)
            settings.EXECUTION_BAN_TASKS.add(settings.TAPSWAP_TASK_NAME)
            raise Exception(error_message)

        data = json.loads(content)
        return data

    def get_current_missing_active_missions(self):
        missions = self.conf.get("missions", [])
        allowed_req_types = set(["youtube", "website"])
        missed_missions = {}
        for mission in missions:
            mission_id = mission.get("id")
            if (
                mission_id in self.completed_missions
                and mission_id not in self.just_claim_missions
            ):
                continue
            mission_start = mission.get("start_at")
            mission_end = mission.get("end_at")
            ts_ms = int(time.time() * 1000)
            if mission_start and mission_start and mission_start > ts_ms > mission_end:
                continue
            reqs = mission.get("items", [])
            if len(reqs) != 1:
                continue
            req = reqs[0]
            code = None
            req_type = req.get("type")
            if req_type not in allowed_req_types:
                continue
            req_need_answer = req.get("require_answer")
            code = None
            if req_need_answer:
                code = mission_codes.get(mission_id)
                if not code:
                    missed_missions[mission_id] = mission.get("title")
        return missed_missions

    def choose_mission(self):
        pre_missions = self.conf.get("missions", [])
        allowed_req_types = set(["youtube", "website"])

        missions = pre_missions[:]
        random.shuffle(missions)

        for mission in missions:
            mission_id = mission.get("id")
            if (
                mission_id in self.completed_missions
                and mission_id not in self.just_claim_missions
            ):
                continue
            mission_start = mission.get("start_at")
            mission_end = mission.get("end_at")
            ts_ms = int(time.time() * 1000)
            if mission_start and mission_start and mission_start > ts_ms > mission_end:
                continue
            reqs = mission.get("items", [])
            if len(reqs) != 1:
                continue
            req = reqs[0]
            code = None
            req_type = req.get("type")
            if req_type not in allowed_req_types:
                continue
            req_need_answer = req.get("require_answer")
            code = None
            if req_need_answer:
                code = mission_codes.get(mission_id)
                if not code:
                    continue

            req_wait = req.get("wait_duration_s")
            return {
                "id": mission_id,
                "type": req_type,
                "needcode": req_need_answer,
                "code": code,
                "wait": req_wait,
            }

    async def join_mission(self, mission_id):
        url = "https://api.tapswap.club/api/missions/join_mission"
        headers = self.get_api_headers(bearer=True)
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p={"id": mission_id},
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        await self.sleep_after_request()
        status = request.get("status")
        content = request.get("content")
        self.logger.info(
            f"POST Challenge page status: {status}. Content len: {len(content)}"
        )
        data = json.loads(content)
        active_missions = [
            i.get("id")
            for i in data.get("account", {}).get("missions", {}).get("active", [])
        ]
        if mission_id not in active_missions:
            raise Exception(f"Failed to join mission. Mission id: {mission_id}")
        else:
            self.logger.info(f"Successful join mission id: {mission_id}")

    def is_mission_verified(self, data, mission_id):
        current_mission_status = {}
        for mission_status in (
            data.get("account", {}).get("missions", {}).get("active", [])
        ):
            if mission_status.get("id") == mission_id:
                current_mission_status = mission_status
                break
        items = current_mission_status.get("items", [])
        verified = None
        for item in items:
            if verified is None:
                verified = verified or item.get("verified", False)
            else:
                verified = verified and item.get("verified", False)
        self.logger.info(f"Mission {mission_id} verified status: {verified}")
        return verified

    async def finish_mission_item(self, mission_id: str, user_input: str = None):
        url = "https://api.tapswap.club/api/missions/finish_mission_item"
        headers = self.get_api_headers(bearer=True)
        payload = {"id": mission_id, "itemIndex": 0}
        if user_input:
            payload["user_input"] = user_input
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201, 400],
            logger=self.logger,
            retry_count=1,
        )
        status = request.get("status")
        if status == 400:
            self.logger.error(
                f"Looks like wrong code for {mission_id}, code: {user_input}"
            )
            return
        content = request.get("content")
        self.logger.info(f"Finish mission item status: {status}")
        data = json.loads(content)
        verified = self.is_mission_verified(data, mission_id)
        return verified

    async def finish_mission(self, mission_id):
        url = "https://api.tapswap.club/api/missions/finish_mission"
        headers = self.get_api_headers(bearer=True)
        payload = {"id": mission_id}
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.info(f"Finish mission status: {status}")
        data = json.loads(content)
        completed_missions = (
            data.get("account", {}).get("missions", {}).get("completed", [])
        )
        if mission_id not in completed_missions:
            raise Exception(f"Mission {mission_id} not in completed missions: {data}")
        return True

    async def claim_mission_reward(self, mission_id):
        url = "https://api.tapswap.club/api/player/claim_reward"
        headers = self.get_api_headers(bearer=True)
        payload = {"task_id": mission_id}
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.info(f"Claim status: {status}")

    async def complete_mission_data(self, mission_data):

        self.logger.info(f"Start doing mission: {mission_data}")
        mission_id = mission_data.get("id")
        mission_type = mission_data.get("type")
        mission_needcode = mission_data.get("needcode")
        mission_code = mission_data.get("code")
        mission_wait = mission_data.get("wait")

        if mission_id in self.just_claim_missions:
            self.logger.info(f"Mission {mission_id} all time waiting for claim!")
            await self.claim_mission_reward(mission_id)
            return

        verified = self.is_mission_verified(self.account_data, mission_id)
        if verified is None:
            if not mission_id in self.active_missions:
                await self.join_mission(mission_id)
            else:
                self.logger.info(f"Mission {mission_id} started before")

        if verified is None:
            self.logger.info("Init first finish mission item without params")
            verified = await self.finish_mission_item(mission_id, user_input=None)
            self.logger.info(
                f"Finish first finish mission item without params. Verified: {verified}"
            )
        if not verified and verified is False:
            if mission_needcode and mission_wait and mission_code:
                await self.sleep_after_request(mission_wait + 10, mission_wait + 20)
                self.logger.info(
                    f"Init second finish mission item with param: {mission_code}"
                )
                verified = await self.finish_mission_item(
                    mission_id, user_input=mission_code
                )
            else:
                await self.sleep_after_request(30, 40)
                self.logger.info("Init second finish mission item without params")
                verified = await self.finish_mission_item(mission_id, user_input=None)
        else:
            self.logger.error(
                f"Mission {mission_id} - verify status after first finish mission item still {verified}. Initialized before."
            )
        if verified:
            completed = await self.finish_mission(mission_id)
            if completed:
                await self.claim_mission_reward(mission_id)
        else:
            self.logger.error(f"Mission {mission_id} still not verified.")

    async def complete_mission(self):
        mission_to_complete = self.choose_mission()
        if mission_to_complete:
            await self.complete_mission_data(mission_to_complete)
        else:
            self.logger.info("No missions to complete.")

    async def submit_taps(self, taps_session_finish_ts_ms, taps_count):
        # if have boost -> activate it
        # after function if have restore charge -> activate it

        url = "https://api.tapswap.club/api/player/submit_taps"
        headers = self.get_api_headers(bearer=True)
        self.logger.debug("Start selenium compute Content-Id")
        headers["Content-Id"] = str(
            self.selen.browser.execute_script(
                f"return {taps_session_finish_ts_ms} * {self.telegram_user_id} % {self.telegram_user_id}"
            )
        )
        self.logger.debug("Finish selenium compute Content-Id")
        payload = {"taps": taps_count, "time": taps_session_finish_ts_ms}
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.info(
            f"Submited {taps_count} taps in {taps_session_finish_ts_ms} ts_ms. Status: {status}"
        )
        data = json.loads(content)

        self.my_shares = data.get("player", {}).get("shares")

        return data.get("player", {}).get("energy", 0)

    async def make_taps(self):
        # energy_level = self.account_data['player'].get('energy_level')

        tap_level = self.account_data["player"].get("tap_level")
        energy = self.account_data["player"].get("energy", 0)
        energy_tap_cost = self.tap_level_config[tap_level - 1].get("energy")

        charge_level = self.account_data["player"].get("charge_level")
        energy_restore_per_second = self.charge_levels_config[charge_level - 1].get(
            "rate"
        )
        energy_tap_stop = energy_restore_per_second * random.randint(10, 15)
        while energy > energy_tap_stop:

            taps_current_session = random.randint(90, 105)
            taps_cost_current_session = int(energy_tap_cost * taps_current_session)

            if energy - taps_cost_current_session <= 0:
                taps_current_session = int(energy / energy_tap_cost)
                taps_per_second = random.randint(5000, 6000) / 1000
                taps_time_current_session = (
                    int(taps_current_session / taps_per_second * 100) / 100
                )
            else:
                taps_time_current_session = random.randint(15000, 16000) / 1000
            self.logger.debug(
                f"GO SLEEP. Time: {taps_time_current_session} sec. ENERGY: {energy}. Tap cost: {energy_tap_cost}. Taps: {taps_current_session}."
            )
            await asyncio.sleep(taps_time_current_session)
            taps_session_finish_ts_ms = int(time.time() * 1000)
            energy = await self.submit_taps(
                taps_session_finish_ts_ms, taps_current_session
            )

    async def install_user_upgrade(self, upgrade_type: str):
        url = "https://api.tapswap.club/api/player/upgrade"
        headers = self.get_api_headers(bearer=True)
        payload = {"type": upgrade_type}
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.info(f"Installed user upgrade {upgrade_type}. Status: {status}")
        data = json.loads(content)

        player = data.get("player", {})

        self.my_shares = player.get("shares")
        self.my_blocks = player.get("blocks")
        self.my_videos = player.get("videos")
        self.my_crystals = player.get("crystals")

    async def upgrade_taps(self):
        tap_level = self.account_data["player"].get("tap_level")
        charge_level = self.account_data["player"].get("charge_level")
        energy_level = self.account_data["player"].get("energy_level")

        if energy_level < len(self.energy_levels_config):
            energy_update_price = self.energy_levels_config[energy_level - 1].get(
                "price"
            )
            if self.my_shares >= energy_update_price:
                self.logger.debug(
                    f"Installing user upgrade ENERGY. Shares: {self.my_shares}. Current level: {energy_level}"
                )
                await self.install_user_upgrade("energy")
                await self.sleep_after_request(3, 10)

        if tap_level < len(self.tap_level_config):
            tap_update_price = self.tap_level_config[tap_level - 1].get("price")
            if self.my_shares >= tap_update_price:
                self.logger.debug(
                    f"Installing user upgrade TAP. Shares: {self.my_shares}. Current level: {tap_level}"
                )
                await self.install_user_upgrade("tap")
                await self.sleep_after_request(3, 10)

        if charge_level < len(self.charge_levels_config):
            charge_update_price = self.charge_levels_config[charge_level - 1].get(
                "price"
            )
            if self.my_shares >= charge_update_price:
                self.logger.debug(
                    f"Installing user upgrade CHARGE. Shares: {self.my_shares}. Current level: {charge_level}"
                )
                await self.install_user_upgrade("charge")
                await self.sleep_after_request(3, 10)

    async def emulate_app_start(
        self,
    ):  # TODO SOLVE CHALLENGE IN DIFFERENT BROWSER WINDOWS
        # LOOP FREEZE ON SOME SYNCRONEOUS FUNCTION
        await self.load_main_page()

        chq_encoded_challenge = await self.login()
        challenge_answer = self.solve_challenge(chq_encoded_challenge)
        self.cache_id = challenge_answer.get("cache_id")

        self.account_data = await self.challenge(chq_challenge=challenge_answer)
        self.bearer = self.account_data.get("access_token")
        self.logger.info(f"Got Bearer: {self.bearer}")
        if not self.bearer:
            raise Exception("Got bad bearer token. Exitting...")

        self.my_shares = self.account_data.get("player", {}).get("shares", 0)
        self.my_blocks = self.account_data.get("player", {}).get("blocks", 0)
        self.my_videos = self.account_data.get("player", {}).get("videos", 0)
        self.my_crystals = self.account_data.get("player", {}).get("crystals", 0)

        missions = self.account_data.get("account", {}).get("missions", {})
        self.completed_missions = missions.get("completed", [])
        self.active_missions = [i.get("id") for i in missions.get("active", [])]
        self.just_claim_missions = self.account_data.get("player", {}).get("claims", [])

        self.conf = self.account_data.get("conf", {})
        self.energy_levels_config = self.conf.get("energy_levels", [])
        self.charge_levels_config = self.conf.get("charge_levels", [])
        self.tap_level_config = self.conf.get("tap_levels", [])

    async def upgrade_building(self, building_id):
        url = "https://api.tapswap.club/api/town/upgrade_building"
        headers = self.get_api_headers(bearer=True)

        payload = {
            "building_id": building_id,
        }
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        data = json.loads(content)

        next_level = data.get("next_level")
        player = data.get("player", {})

        self.my_shares = player.get("shares")
        self.my_blocks = player.get("blocks")
        self.my_videos = player.get("videos")
        self.my_crystals = player.get("crystals")

        self.logger.info(
            f"Building {building_id} upgrade queued. Status: {status}. Next level: {next_level}"
        )

    async def build(self):
        my_town = self.account_data.get("player", {}).get("town", {})
        worker_count = my_town.get("builders", 0)
        ts_current_ms = int(time.time() * 1000)
        my_buildings = my_town.get("buildings", [])

        currently_under_constuction = []
        current_my_buildings_level = {}
        for b in my_buildings:
            building_id = b.get("id")
            building_level = b.get("level")
            building_ready_at = b.get("ready_at")
            if ts_current_ms < building_ready_at:
                worker_count -= 1
                currently_under_constuction.append(building_id)
                left_time_s = int((building_ready_at - ts_current_ms) / 1000)
                self.logger.info(
                    f"Building {building_id} is still updating to level {building_level}. Left: {left_time_s} sec."
                )
                current_my_buildings_level[building_id] = building_level - 1
            else:
                current_my_buildings_level[building_id] = building_level

        buildings_plan = self.conf.get("town", {}).get("buildings", [])
        while worker_count > 0:
            some_building_builded = None
            for b in buildings_plan:
                building_id = b.get("id")
                current_building_level = current_my_buildings_level.get(building_id, 0)
                # если это здание уже строится - пропускаем его
                if building_id in currently_under_constuction:
                    continue
                building_levels = b.get("levels", [])
                upgrade_info = building_levels[2]

                updgrade_info_known_keys = set(
                    [
                        "rate",
                        "cost",
                        "time_s",
                        "reward",
                        "check_telegram",
                        "required",
                    ]
                )

                upgrade_info_keys = set(upgrade_info.keys())

                new_keys = upgrade_info_keys - updgrade_info_known_keys
                if new_keys:
                    self.logger.error(
                        f"Detected unknown keys: {new_keys}. Building: {building_id}. Current level: {current_building_level}"
                    )
                    continue

                # check if user is subscribet to channel ETIX EBANUX SOBAK
                upgrade_check_channel = upgrade_info.get("check_telegram")
                if upgrade_check_channel:
                    user_subscribed = await self.db.check_or_create_subscribe_task(
                        number=self.telegram_session_id, channel=upgrade_check_channel
                    )
                    if not user_subscribed:
                        continue

                # check if we have enouth moneyyyyy
                upgrade_cost = upgrade_info.get("cost")
                upgrade_cost_shares = upgrade_cost.get("shares", 0)
                upgrade_cost_blocks = upgrade_cost.get("blocks", 0)
                upgrade_cost_videos = upgrade_cost.get("videos", 0)
                if not (
                    self.my_shares >= upgrade_cost_shares
                    and self.my_blocks >= upgrade_cost_blocks
                    and self.my_videos >= upgrade_cost_videos
                ):
                    continue

                # check if we have req buildings
                upgrade_requirements = upgrade_info.get("required", {})
                if upgrade_requirements:
                    required_building_id = upgrade_requirements.get("id")
                    if current_my_buildings_level.get(
                        required_building_id, 0
                    ) < upgrade_requirements.get("level"):
                        continue

                await self.upgrade_building(building_id)
                await self.sleep_after_request(3, 10)
                worker_count -= 1
                currently_under_constuction.append(building_id)
                some_building_builded = True
                break
            if not some_building_builded:
                self.logger.info("No buildings can be builded. Passed this moment.")
                break

    async def sleep_after_request(self, sleep_min=14, sleep_max=18):
        await asyncio.sleep(random.randint(100 * sleep_min, 100 * sleep_max) / 100)

    async def make_actions(self):
        await self.emulate_app_start()

        # # 90% to make taps
        # if random.randint(0, 100) > 10:
        #     await self.make_taps()
        await self.sleep_after_request()
        # 80% to build smth
        if random.randint(0, 100) > 20:
            await self.build()
        # 70% to complete mission
        if random.randint(0, 100) > 30:
            await self.complete_mission()
        await self.sleep_after_request()
        # 60% to upgrade taps
        if random.randint(0, 100) > 40:
            await self.upgrade_taps()

        self.logger.info(
            f"Job finish. Shares: {self.my_shares}, blocks: {self.my_blocks}, videos: {self.my_videos}, crystals: {self.my_crystals}"
        )
        await self.db.set_tapswap_balance(
            number=self.telegram_session_id,
            shares=self.my_shares,
            blocks=self.my_blocks,
            videos=self.my_videos,
            crystals=self.my_crystals,
        )


async def main():
    proxy = "07196708-zone-custom-region-CA-city-toronto-sessid-RoRsgvQB-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    webpp_url = "https://app.tapswap.club/?bot=app_bot_2#tgWebAppData=query_id%3DAAGSK95WAwAAAJIr3lbl9Zoi%26user%3D%257B%2522id%2522%253A7899851666%252C%2522first_name%2522%253A%2522Sandraafv%2522%252C%2522last_name%2522%253A%2522Stoll%2522%252C%2522username%2522%253A%2522JVHMWF%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252FV6SCog24y4KYHscl4z6-StMRhQtCl8Hpn9UQwwhTZR-gTceynxZjRMV7mntY1nCG.svg%2522%257D%26auth_date%3D1733750288%26signature%3Dd17u_gy5pTGdUH_tV46zIYySepMHqB87im1qBRI3_8wqAiYQuDCw9kmXlBIcCTPvCB9tSYbciFKbM7Tk0N-MCg%26hash%3D46d3ddeeed7458fcda7e4601195758a5c94bbf81081d908da39fd39700472c7e&tgWebAppVersion=7.10&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    sb = secure_browser.SecChromeBrowser(headless=True)

    db = dbutils.TDB(settings.db_path)

    start_dt = datetime.datetime.now()

    ts = TapswapActions(
        web_app_entry_url=webpp_url,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        telegram_user_id=7899851666,
        telegram_session_id="27682481559",
        selen=sb,
        db=db,
        worker_start_datetime=start_dt,
    )

    await ts.emulate_app_start()
    await ts.upgrade_taps()
    # await ts.make_actions()
    # missing_missions = ts.get_current_missing_active_missions()
    # mm_json = json.dumps(missing_missions, indent=4)
    # print(mm_json)

    pass
    # await ts.complete_mission()
    # if its night -> not tap -> not missions
    # if day -> tap with prob 70% and complete mission with 50%

    # await ts.make_taps()
    # await ts.build()


if __name__ == "__main__":
    asyncio.run(main())

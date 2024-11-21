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

HTTP_REQUEST_TIMEOUT = 30

X_APP = "tapswap_server"
X_CV = "662"
X_TOUCH = "1"

mission_codes = {
    "M2325": "7s3pu",
    "M2326": "1s5t9",
    "M2327": "6tseg",
    "M2328": "4tsf",
    "M2329": "s7u3",
    "M2330": "7snq",
    "M2331": "s6ur",
    "M2332": "unfi",
    "M2334": "quis",
    "M2335": "3y9wa",
    "M2336": "4a1b7",
    "M2337": "4t8a",
    "M2338": "8t1r3",
    "M2339": "4b5n2",
    "M2340": "9u2b3",
    "M2341": "perr",
    "M2342": "urm1",
    "M2343": "aabily",
    "M2344": "iti8",
    "M2345": "28r1e",
    "M2346": "2le6c",
    "M2347": "91ki",
    "M2348": "3po7e",
    "M2349": "1tefy",
    "M2350": "5str",
    "M2352": "ued6",
    "M2353": "ait7y",
    "M2354": "2o4n6",
    "M2355": "6yta",
    "M2356": "7oin2",
    "M2357": "76n2g",
    "M2358": "wo9p1",
    "M2359": "8tgz",
    "M2360": "4ate1",
    "M2361": "puter",
    "M1265": "9(&TR",
    "M1266": "&gRe8",
    "M1267": "hg8#2",
    "M1268": "3N4+T",
    "M1269": "2Vb&E",
    "M1270": "5F0Lm",
    "M1271": "3Nm&p",
    "M1272": "9*JR$",
    "M1273": "KF7y4",
    "M1274": "H9#ka",
    "M1275": "3#DaP",
    "M1276": "5$%hG",
    "M1277": "3Tp&e",
    "M1278": "3Aqw$",
    "M1279": "@R#7Y",
    "M1280": "8GpnM",
    "M1281": "Ey*Nb",
    "M2363": "s7ug",
    "M2364": "4can",
    "M2365": "2c8h",
    "M2366": "cashtoken",
    "M2367": "ce7n7",
    "M2368": "p66i",
    "M2369": "grad",
    "M2370": "h3el",
    "M2371": "morn",
    "M2372": "6tue",
    "M2373": "3orow",
    "M2374": "9ki7r",
    "M2375": "8n3eo",
    "M2376": "7wp4",
    "M2377": "h8a7",
    "M2378": "r5ou",
    "M2379": "h2e7",
    "M2380": "8h1a",
    "M2381": "amaz",
    "M2382": "9va5",
    "M2383": "pitn",
    "M2384": "t6bh",
    "M2385": "9s5h",
    "M2386": "sorship",
    "M2387": "8e2ce",
    "M2388": "uate",
    "M2389": "hpful",
    "M2390": "i8ng",
    "M2391": "sday",
    "M2392": "3tomm",
    "M2393": "nd1er",
    "M1294": "d%98N",
}


class TapswapActions:
    def __init__(
        self,
        web_app_entry_url: str,
        proxy_host="",
        proxy_port=0,
        proxy_user="",
        proxy_password="",
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        logging_name="TapswapActions unnamed",
        telegram_user_id=None,
        selen=None,
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

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
        self.telegram_user_id = telegram_user_id
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
        content = request.get("content")
        self.logger.debug(f"GET main page status: {status}. Len: {len(content)}")

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

    def solve_challenge(self, chq):
        magic_number = 232
        key = 157

        chq_bytes = binascii.unhexlify(chq)
        js = "".join([chr(i ^ 157) for i in chq_bytes])
        js = (
            "var cache_id = ''; window.ctx = {api: {setHeaders : function(t){for(const[i,n]of Object.entries(t))cache_id = n}}};"
            + js
        )
        html_path = "assets/tapswap.html"
        nix_abspath = os.path.abspath(html_path).replace("\\", "/")
        self.selen.browser.get(f"file:///{nix_abspath}")
        js_base64_encoded = base64.b64encode(js.encode()).decode()

        ret = self.selen.browser.execute_script(
            f'jsb64="{js_base64_encoded}"; x = eval(atob(jsb64)); return [x,cache_id];'
        )
        answer, cache_id = ret
        answer += magic_number
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
            f"POST Challenge page status: {status}. Content len: {len(content)}"
        )
        data = json.loads(content)
        return data

    def choose_mission(self, missions):
        allowed_req_types = set(["youtube", "website"])

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
            good_statuses=[200, 201],
            logger=self.logger,
        )
        status = request.get("status")
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
        missions = self.conf.get("missions", [])
        mission_to_complete = self.choose_mission(missions=missions)
        await self.complete_mission_data(mission_to_complete)

    async def submit_taps(self, taps_session_finish_ts_ms, taps_count):
        # if have boost -> activate it
        # after function if have restore charge -> activate it

        url = "https://api.tapswap.club/api/player/submit_taps"
        headers = self.get_api_headers(bearer=True)
        headers["Content-Id"] = str(
            self.selen.browser.execute_script(
                f"return {taps_session_finish_ts_ms} * {self.telegram_user_id} % {self.telegram_user_id}"
            )
        )
        payload = {"taps": taps_count, "time": taps_session_finish_ts_ms}
        request = await notpixel_tools.http_request(
            "POST",
            url,
            headers,
            proxy=self.proxy_string,
            json_p=payload,
            http_timeout=HTTP_REQUEST_TIMEOUT,
            good_statuses=[200, 201, 400],
            logger=self.logger,
        )
        status = request.get("status")
        content = request.get("content")
        self.logger.info(
            f"Submited {taps_count} taps in {taps_session_finish_ts_ms} ts_ms. Status: {status}"
        )
        data = json.loads(content)
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
        energy_tap_stop = energy_restore_per_second * random.randint(6, 9)
        while energy > energy_tap_stop:
            taps_per_second = random.randint(5000, 6000) / 1000
            taps_current_session = random.randint(90, 105)
            taps_cost_current_session = int(energy_tap_cost * taps_current_session)
            if energy - taps_cost_current_session <= 0:
                taps_current_session = int(energy / energy_tap_cost)

            taps_time_current_session = (
                int(taps_current_session / taps_per_second * 100) / 100
            )
            self.logger.debug(
                f"GO SLEEP. Time: {taps_time_current_session} sec. ENERGY: {energy}. Tap cost: {energy_tap_cost}. Taps: {taps_current_session}."
            )
            await asyncio.sleep(taps_time_current_session)
            taps_session_finish_ts_ms = int(time.time() * 1000)
            energy = await self.submit_taps(
                taps_session_finish_ts_ms, taps_current_session
            )

    async def emulate_app_start(self):
        await self.load_main_page()
        chq = await self.login()
        challenge_answer = self.solve_challenge(chq)
        self.cache_id = challenge_answer.get("cache_id")

        self.account_data = await self.challenge(chq_challenge=challenge_answer)
        self.bearer = self.account_data.get("access_token")
        self.logger.info(f"Got Bearer: {self.bearer}")

        missions = self.account_data.get("account", {}).get("missions", {})
        self.completed_missions = missions.get("completed", [])
        self.active_missions = [i.get("id") for i in missions.get("active", [])]
        self.just_claim_missions = self.account_data.get("player", {}).get("claims", [])

        self.conf = self.account_data.get("conf", {})
        self.energy_levels_config = self.conf.get("energy_levels", [])
        self.charge_levels_config = self.conf.get("charge_levels", [])
        self.tap_level_config = self.conf.get("tap_levels", [])

        pass


async def main():
    proxy = "07196708-zone-custom-region-CA-sessid-C9p85mlF-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    webpp_url = "https://app.tapswap.club/?bot=app_bot_0#tgWebAppData=query_id%3DAAEITE4rAAAAAAhMTiu7VFKu%26user%3D%257B%2522id%2522%253A726551560%252C%2522first_name%2522%253A%2522A%2522%252C%2522last_name%2522%253A%2522S%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252F_aefHTTaqquqHSKCJLEG3ibz76vobUxfaln3jrMDe2A.svg%2522%257D%26auth_date%3D1732190955%26signature%3DsqzjNdl9YQezbWHBjRskKSjS_jM7DVHrPJj9G2BKyNNDwiwgjPw7uKIIsTprQfoEWR2a2D8Qqxq3z90t6I9JAg%26hash%3Dee3255412b879235c1792b131a92f0ea6476c7a61dbf70472e280ac49b4d5875&tgWebAppVersion=8.0&tgWebAppPlatform=tdesktop&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    sb = secure_browser.SecChromeBrowser(headless=False)

    ts = TapswapActions(
        web_app_entry_url=webpp_url,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        telegram_user_id=726551560,
        selen=sb,
    )
    await ts.emulate_app_start()
    # await ts.complete_mission()
    # if its night -> not tap -> not missions
    # if day -> tap with prob 70% and complete mission with 50%

    await ts.make_taps()


if __name__ == "__main__":
    asyncio.run(main())

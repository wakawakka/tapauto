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
        self.init_user_agent()

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

    def get_headers_api(
        self,
        origin: str = None,
        referer: str = None,
        token: str = None,
        not_modified_since: datetime.datetime = None,
    ):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.9;q=0.9",
            # "Authorization": f"initData {self.auth_token}",
            "Sec-Fetch-Dest": "empty",
            "sec-fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.user_agent,  # "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36",
            "Priority": "u=1, i",
        }
        if token:
            headers["token"] = token
        if not_modified_since:
            headers["If-Modified-Since"] = self.dt_convert_header(not_modified_since)
        if referer:
            headers["Referer"] = referer
        if origin:
            headers["Origin"] = origin
        return headers

    async def load_main_page(self):
        headers = self.get_headers_api()
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
        self.logger.info(f"GET main page status: {status}. Len: {len(content)}")

    def get_autorization_header(self):
        q, w = self.web_app_entry_url.split("#tgWebAppData=")
        a, s = w.split("&", 1)
        return unquote(a)

    async def login(self, bot_key: str = "app_bot_0", referrer: str = ""):
        url = "https://api.tapswap.club/api/account/login"
        headers = self.get_headers_api(
            origin="https://app.tapswap.club", referer="https://app.tapswap.club/"
        )
        headers["x-app"] = "tapswap_server"
        headers["x-touch"] = "1"
        headers["x-cv"] = "662"
        headers["Cache-Id"] = "".join(
            [random.choice(string.ascii_letters + string.digits) for i in range(8)]
        )
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
        self.logger.info(
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
        headers = self.get_headers_api(
            origin="https://app.tapswap.club", referer="https://app.tapswap.club/"
        )
        headers["Accept"] = "*/*"
        headers["x-app"] = "tapswap_server"
        headers["x-touch"] = "1"
        headers["x-cv"] = "662"
        headers["Content-Type"] = "application/json"

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
            f"POST LOGIN page status: {status}. Content len: {len(content)}"
        )
        data = json.loads(content)
        return data

    async def emulate_app_start(self):
        await self.load_main_page()
        chq = await self.login()
        challenge_answer = self.solve_challenge(chq)
        await self.challenge(chq_challenge=challenge_answer)
        pass


async def main():
    proxy = "07196708-zone-custom-region-CA-sessid-C9p85mlF-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    webpp_url = "https://app.tapswap.club/?bot=app_bot_0#tgWebAppData=user%3D%257B%2522id%2522%253A726551560%252C%2522first_name%2522%253A%2522A%2522%252C%2522last_name%2522%253A%2522S%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252F_aefHTTaqquqHSKCJLEG3ibz76vobUxfaln3jrMDe2A.svg%2522%257D%26chat_instance%3D-8151824430045121425%26chat_type%3Dsender%26auth_date%3D1731999238%26signature%3DrEizT0uDZG8FQC8igZg3dSLopkDjdXPCDkAfe-SXH86p7EM0q93oAFx5NofzSW5oUI8JRSngbBmD3Cwp93FWCw%26hash%3D4c1fd59bdd0f29cf333f98d0b4bbd47f361c2ebd56bf50bbd597222722f76e3b&tgWebAppVersion=8.0&tgWebAppPlatform=tdesktop&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    sb = secure_browser.SecChromeBrowser(headless=False)

    ts = TapswapActions(
        web_app_entry_url=webpp_url,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        selen=sb,
    )
    await ts.emulate_app_start()


if __name__ == "__main__":
    asyncio.run(main())

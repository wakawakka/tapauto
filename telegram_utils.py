import os
import sys
import json
import uuid
import asyncio
import code

from opentele.td import TDesktop
from opentele.tl import TelegramClient as TC_opentele
from opentele.api import API, UseCurrentSession, CreateNewSession

from telethon import TelegramClient as TC_telethon
from telethon.sessions import StringSession
from telethon import functions, types
import socks

import localsettings
import settings


def create_proxychains_conf(path, proxy_host, proxy_port, proxy_user, proxy_password):
    pattern = (
        "strict_chain\n"
        "proxy_dns\n"
        "remote_dns_subnet 224\n"
        "localnet 127.0.0.0/255.0.0.0\n"
        "delete_fake_ip_after_child_exits 1\n"
        "default_target PROXY\n"
        "use_fake_ip_when_hostname_not_matched 1\n"
        "map_resolved_ip_to_host 0\n"
        "search_for_host_by_resolved_ip 0\n"
        "resolve_locally_if_match_hosts 1\n"
        "gen_fake_ip_using_hashed_hostname 0\n"
        "first_tunnel_uses_ipv4 1\n"
        "first_tunnel_uses_ipv6 0\n"
        "log_level 400\n"
        "[ProxyList]\n"
        f"socks5 {proxy_host} {proxy_port} {proxy_user} {proxy_password}\n"
    )
    written = 0
    with open(path, "w") as f:
        written = f.write(pattern)
    return written > 0


class Telega:

    def __init__(
        self,
        session_id,
        proxy: bool,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_password: str,
        telegram_cache_dir,
    ):
        self.cache_dir = telegram_cache_dir
        self.session_dir = os.path.join(self.cache_dir, session_id)
        self.session_file = os.path.join(self.session_dir, f"{session_id}.session")
        os.makedirs(self.session_dir, exist_ok=True)

        self.telethon_proxy = None
        if proxy:
            self.telethon_proxy = {
                "proxy_type": "socks5",
                "addr": proxy_host,
                "port": proxy_port,
                "username": proxy_user,
                "password": proxy_password,
                "rdns": True,
            }

        self.session_id = session_id

        self.client = None
        self.loop = asyncio.get_event_loop()
        # if not session_id:
        #     self.session_id = str(uuid.uuid4())

    # ONLY WINDOWS MODE

    def init_client_tdata(
        self, tdata_path, platform="desktop", hardware_id="228", password=None
    ):
        self.loop.run_until_complete(
            self.__a_init_client_tdata(tdata_path, platform, hardware_id, password)
        )

    async def __a_init_client_tdata(
        self,
        tdata_path,
        platform,
        hardware_id,  # used for fake "UserAgent" must be constant like a proxy
        password,
    ):
        if self.client:
            raise Exception("Client already created.")

        match platform:
            case "desktop":
                preapi = API.TelegramDesktop
            case "ios":
                preapi = API.TelegramIOS
            case "macos":
                preapi = API.TelegramMacOS
            case "android":
                preapi = API.TelegramAndroid
            case _:
                raise Exception('Platform variants: "desktop, ios, macos, android"')

        api = preapi.Generate(unique_id=hardware_id)
        tdesk = TDesktop(tdata_path)
        assert tdesk.isLoaded()
        self.client = await TC_opentele.FromTDesktop(
            tdesk,
            session=self.session_file,
            flag=UseCurrentSession,
            api=api,
            password=password,
            proxy=self.telethon_proxy,
        )
        await self.client.connect()

    def init_client_api(self, api_id, api_hash, phone=None):
        self.loop.run_until_complete(self.__a_init_client_api(api_id, api_hash, phone))

    async def __a_init_client_api(self, api_id, api_hash, phone):
        if self.client:
            raise Exception("Client already created.")
        if isinstance(api_id, str):
            api_id = int(api_id)
        self.client = TC_telethon(
            session=self.session_file,
            api_id=api_id,
            api_hash=api_hash,
            proxy=self.telethon_proxy,
        )
        TC_telethon()
        await self.client.connect()
        auth_success = (
            await self.client.is_user_authorized()
        )  # try to auth via initial session file
        if not auth_success:
            # try to auth via telegram desktop
            user_phone = phone
            if not phone:
                user_phone = input("Enter your phone: ")
            print(f"First run. Sending code request to Telegram Account {user_phone}")
            await self.client.sign_in(user_phone)
            self_user = None
            while self_user is None:
                code = input("Enter the code you just received: ")
                self_user = await self.client.sign_in(code=code)
            auth_success = await self.client.is_user_authorized()
        me = await self.client.get_me()
        print(f"Logged in as {me.phone} ({me.id})")
        return auth_success

    async def check_client_auth(self):
        if self.client:
            auth = await self.client.is_user_authorized()
            if not auth:
                raise Exception(f"Session {self.session_id} not authorized")

    def start_bot(self, bot_username, param="start"):
        self.client.loop.run_until_complete(self.__a_start_bot(bot_username, param))

    async def __a_start_bot(self, bot_username, param):
        await self.check_client_auth()
        bot = await self.client.get_entity(bot_username)
        result = await self.client(
            functions.messages.StartBotRequest(
                bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                start_param=param,
            )
        )
        result_data = json.loads(result.to_json())

    def get_bot_webapp(
        self, bot_username: str, platform: str, url: str, param: str | None = None
    ):
        res = self.client.loop.run_until_complete(
            self.__a_get_bot_webapp(bot_username, platform, url, param)
        )
        return res

    async def __a_get_bot_webapp(self, bot_username, platform, url, param):
        await self.check_client_auth()
        bot = await self.client.get_entity(bot_username)
        result = await self.client(
            functions.messages.RequestWebViewRequest(
                bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                platform=platform,
                from_bot_menu="YES",
                start_param=param,
                url=url,
            )
        )
        return result.url

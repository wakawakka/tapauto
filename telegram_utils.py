import logging
import os
import time
import datetime

from async_timeout import timeout
from telethon import TelegramClient as TC_telethon
from telethon import functions, types

import utils
from exceptions import TelegramBadConvertProfile, TelegramBadProfile
from opentele.api import API, CreateNewSession, UseCurrentSession
from opentele.td import TDesktop
from opentele.tl import TelegramClient as TC_opentele

PROFILE_LOAD_TIMEOUT = 5
CONNECT_TIMEOUT = 15
REQUEST_TIMEOUT = 10


class Telega:

    def __init__(
        self,
        telegram_cache_dir,
        session_id,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_password: str,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
        name="Telega unnamed",
        remove_old_session_file=True,
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=name
        )

        self.cache_dir = telegram_cache_dir
        self.session_dir = os.path.join(self.cache_dir, session_id)
        os.makedirs(self.session_dir, exist_ok=True)

        self.session_file = os.path.join(self.session_dir, f"{session_id}.session")
        if remove_old_session_file and os.path.isfile(self.session_file):
            os.remove(self.session_file)

        self.telethon_proxy = None
        if proxy_host:
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
        self.app_url = None

    # ONLY WINDOWS MODE
    async def init_client_tdata(
        self,
        tdata_path,
        platform="desktop",
        hardware_id="228",  # used for fake "UserAgent" must be constant like a proxy
        password=None,
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

        async with timeout(PROFILE_LOAD_TIMEOUT):
            try:
                tdesk = TDesktop(tdata_path)
                assert tdesk.isLoaded()
            except BaseException as e:
                raise TelegramBadProfile(tdata_path, e, self.logger)
        self.logger.info(f"Telegram profile loaded - path: {tdata_path}")

        async with timeout(CONNECT_TIMEOUT):
            try:
                self.client = await TC_opentele.FromTDesktop(
                    tdesk,
                    session=self.session_file,
                    flag=CreateNewSession,
                    api=api,
                    password=password,
                    proxy=self.telethon_proxy,
                )
                acc_info = await self.client.get_me()
                assert acc_info
            except BaseException as e:
                raise TelegramBadConvertProfile(tdata_path, e, self.logger)
        self.logger.info(
            f"Telegram profile connect success - path: {tdata_path}, "
            f"id: {acc_info.id}, username: {acc_info.username}, phone: {acc_info.phone}"
        )

    async def init_client_api(self, api_id, api_hash, phone=None):
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

    async def start_bot(self, bot_username, param="start"):
        self.logger.info(f"Telegram bot not started yet. Trying start...")
        bot = await self.client.get_entity(bot_username)
        self.logger.info(f"Got bot entity, id: {bot.id}")
        result_start = await self.client(
            functions.messages.StartBotRequest(
                bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                start_param=param,
            )
        )
        events_s = [i.get("_") for i in result_start.to_dict().get("updates")]
        self.logger.info(f"Api StartBotRequest events: id: {events_s}")
        # result_init_message = await self.client.send_message(
        #     entity=bot, message="/start"
        # )
        # self.logger.info(f"Sent duplicate message: {result_init_message.message}")
        pass

    async def get_bot_webapp(
        self, bot_username: str, platform: str, url: str, param: str = None
    ):
        self.logger.info(
            f"Getting bot web application URL for {bot_username}, {platform}, {url} with params {param}"
        )
        bot = await self.client.get_entity(bot_username)
        self.logger.info(f"Got bot entity, id: {bot.id}")
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
        self.logger.info(f"Got bot web application URL: {result.url}")
        self.app_url = result.url
        self.app_url_dt = datetime.datetime.now()
        return result.url

import logging
import os
import time
import datetime
import asyncio
import random
import json

import socks
from telethon import TelegramClient as TC_telethon
from telethon import functions, types

import utils
from exceptions import TelegramBadConvertProfile, TelegramBadProfile
from opentele_mod.api import API, CreateNewSession, UseCurrentSession
from opentele_mod.td import TDesktop
from opentele_mod.tl import TelegramClient as TC_opentele

PROFILE_LOAD_TIMEOUT = 5
CONNECT_TIMEOUT = 120
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
        logging_name="Telega unnamed",
    ):
        self.logger = utils.get_logger(
            filepath=logfile_path, level=logging_level, name=logging_name
        )

        self.cache_dir = telegram_cache_dir
        self.session_dir = os.path.join(self.cache_dir, session_id)
        os.makedirs(self.session_dir, exist_ok=True)

        self.session_file = os.path.join(self.session_dir, f"{session_id}.session")
        if os.path.isfile(self.session_file):
            self.use_session_flag = UseCurrentSession
        else:
            self.use_session_flag = CreateNewSession
            # os.remove(self.session_file)

        self.telethon_proxy = None
        if proxy_host:
            self.telethon_proxy = {
                "proxy_type": socks.SOCKS5,
                "addr": proxy_host,
                "port": proxy_port,
                "username": proxy_user,
                "password": proxy_password,
                "rdns": True,
            }

        self.session_id = session_id
        self.client = None
        self.app_url = None
        self.app_url_dt = None
        self.bot_started = False

    def get_api_by_platform(self, platform: str):
        match platform:
            case "desktop":
                api_gen = API.TelegramDesktop
            case "ios":
                api_gen = API.TelegramIOS
            case "macos":
                api_gen = API.TelegramMacOS
            case "android":
                api_gen = API.TelegramAndroid
            case _:
                raise Exception('Platform variants: "desktop, ios, macos, android"')
        return api_gen

    # ONLY WINDOWS MODE
    async def init_client_tdata(
        self,
        tdata_path,
        platform="desktop",
        hardware_id="228",  # used for fake "UserAgent" must be constant like a proxy
        password=None,
    ):

        self.tdata_path = tdata_path
        self.platform = platform
        self.hardware_id = hardware_id
        self.password = password

        api_gen = self.get_api_by_platform(platform)
        api = api_gen.Generate(unique_id=hardware_id)

        async with asyncio.timeout(PROFILE_LOAD_TIMEOUT):
            try:
                tdesk = TDesktop(tdata_path)
                assert tdesk.isLoaded()
            except BaseException as e:
                raise TelegramBadProfile(tdata_path, e, self.logger)
        self.logger.info(f"Telegram profile loaded - path: {tdata_path}")

        async with asyncio.timeout(CONNECT_TIMEOUT):
            try:
                self.client = await TC_opentele.FromTDesktop(
                    tdesk,
                    session=self.session_file,
                    flag=self.use_session_flag,
                    api=api,
                    password=password,
                    proxy=self.telethon_proxy,
                )
                if not self.client.is_connected():
                    await self.client.connect()
                acc_info = await self.client.get_me()
                self.logger.info(
                    f"Telegram profile connect success - path: {tdata_path}, "
                    f"id: {acc_info.id}, username: {acc_info.username}, phone: {acc_info.phone}"
                )
            # except asyncio.exceptions.CancelledError as e:

            except BaseException as e:
                if not self.use_session_flag == UseCurrentSession:
                    raise TelegramBadConvertProfile(tdata_path, e, self.logger)
                self.logger.error(
                    "Create telethon session from TDATA with UseCurrentSession failed. Trying to remove old session and create NEW"
                )
                self.use_session_flag = CreateNewSession
                if not self.client.disconnected:
                    await self.client.disconnect()
                    if os.path.isfile(self.session_file):
                        os.remove(self.session_file)
                    del self.client
                    await self.init_client_tdata(
                        tdata_path, platform, hardware_id, password
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
            self.logger.info(
                f"First run. Sending code request to Telegram Account {user_phone}"
            )
            await self.client.sign_in(user_phone)
            self_user = None
            while self_user is None:
                code = input("Enter the code you just received: ")
                self_user = await self.client.sign_in(code=code)
            auth_success = await self.client.is_user_authorized()
        me = await self.client.get_me()
        self.logger.info(f"Logged in as {me.phone} ({me.id})")
        return auth_success

    async def start_bot(self, bot_username, param="start"):
        await self.check_auth(try_reauth=True)

        bot = await self.client.get_entity(bot_username)
        self.logger.info(f"Got bot entity, id: {bot.id}")
        bot_messages = await self.client.get_messages(bot)
        for message in bot_messages:
            if message.text and message.text.startswith("/start"):
                self.logger.info(
                    f"Telegram bot @{bot_username} have started yet. All is OK"
                )
                return

        self.logger.info(
            f"Telegram bot @{bot_username} not started yet. Trying start..."
        )
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

    async def check_auth(self, try_reauth=True):
        auth_ok = await self.client.is_user_authorized()
        msg = f"Check_auth AUTH: {auth_ok}"
        self.logger.debug(msg)
        if not auth_ok:
            error_message = "Client not authorized"
            self.logger.error(error_message)
            if try_reauth:
                self.logger.info("Trying to reauth client with UseCurrentSession flag")
                self.use_session_flag = UseCurrentSession
                await self.init_client_tdata(
                    self.tdata_path, self.platform, self.hardware_id, self.password
                )
            else:
                raise Exception(msg)

    async def get_bot_webapp(self, bot_username: str, platform: str, param=None):
        await self.check_auth(try_reauth=True)
        await self.start_bot(bot_username)
        self.logger.info(
            f"Getting bot web application URL for {bot_username}, {platform}, with params {param}"
        )
        bot = await self.client.get_entity(bot_username)

        self.logger.info(f"Got bot entity, id: {bot.id}")
        # result = await self.client(
        #     functions.messages.RequestWebViewRequest(
        #         bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
        #         peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
        #         platform=platform,
        #         from_bot_menu=False,
        #         compact=False,
        #         start_param=param,
        #         url=url,
        #     )
        # )

        bot_user = types.InputUser(bot.id, bot.access_hash)

        bot_app = await self.client(
            functions.messages.GetBotAppRequest(
                app=types.InputBotAppShortName(bot_id=bot_user, short_name="app"),
                hash=1229,
            )
        )
        input_bot_app = types.InputBotAppID(bot_app.app.id, bot_app.app.access_hash)
        theme_styles = {
            "accent_text_color": "#168acd",
            "bg_color": "#ffffff",
            "bottom_bar_bg_color": "#ffffff",
            "button_color": "#40a7e3",
            "button_text_color": "#ffffff",
            "destructive_text_color": "#d14e4e",
            "header_bg_color": "#ffffff",
            "hint_color": "#999999",
            "link_color": "#168acd",
            "secondary_bg_color": "#f1f1f1",
            "section_bg_color": "#ffffff",
            "section_header_text_color": "#168acd",
            "section_separator_color": "#e7e7e7",
            "subtitle_text_color": "#999999",
            "text_color": "#000000",
        }
        result = await self.client(
            functions.messages.RequestAppWebViewRequest(
                app=input_bot_app,
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                platform=platform,
                # from_bot_menu=False,
                # compact=False,
                start_param=param,
                theme_params=types.TypeDataJSON(json.dumps(theme_styles)),
            )
        )
        self.logger.info(f"Got bot web application URL: {result.url}")
        self.app_url = result.url
        self.app_url_dt = datetime.datetime.now()
        return result.url

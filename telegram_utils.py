import os

from opentele.td import TDesktop
from opentele.tl import TelegramClient as TC_opentele
from opentele.api import API, UseCurrentSession, CreateNewSession

from telethon import TelegramClient as TC_telethon
from telethon import functions, types


class Telega:

    def __init__(
        self,
        telegram_cache_dir,
        session_id,
        proxy_host: str,
        proxy_port: int,
        proxy_user: str,
        proxy_password: str,
    ):
        self.cache_dir = telegram_cache_dir
        self.session_dir = os.path.join(self.cache_dir, session_id)
        self.session_file = os.path.join(self.session_dir, f"{session_id}.session")
        os.makedirs(self.session_dir, exist_ok=True)

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
        tdesk = TDesktop(tdata_path)
        assert tdesk.isLoaded()
        print("PASSWORD:", password)
        self.client = await TC_opentele.FromTDesktop(
            tdesk,
            session=self.session_file,
            flag=CreateNewSession,
            api=api,
            password=password,
            proxy=self.telethon_proxy,
        )
        await self.client.connect()

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

    async def start_bot(self, bot_username, param="start"):
        await self.check_client_auth()
        bot = await self.client.get_entity(bot_username)
        result_start = await self.client(
            functions.messages.StartBotRequest(
                bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                start_param=param,
            )
        )
        result_init_message = await self.client.send_message(
            entity=bot, message="Hello bebe!"
        )

    async def get_bot_webapp(
        self, bot_username: str, platform: str, url: str, param: str = None
    ):
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

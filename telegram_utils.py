import os
import json
import socks
import code

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions, types

import localsettings
import settings


class Telega:

    def __init__(
        self,
        api_id: str,
        api_hash: str,
        phone = None,
        session_id = None,
        proxy: dict = None,
    ):
        # proxy = {
        #     'proxy_type': 'socks5', # (mandatory) protocol to use (see above)
        #     'addr': '1.1.1.1',      # (mandatory) proxy IP address
        #     'port': 5555,           # (mandatory) proxy port number
        #     'username': 'foo',      # (optional) username if the proxy requires auth
        #     'password': 'bar',      # (optional) password if the proxy requires auth
        #     'rdns': True            # (optional) whether to use remote or local resolve, default remote
        # }
        self.phone = phone
        self.session_file = os.path.join(
            settings.session_file_dir, f"{session_id}.session"
        )
        self.client = TelegramClient(self.session_file, api_id, api_hash, proxy=proxy)
        self.login()
        pass

    async def __a_login(self):
        await self.client.connect()
        auth_success = (
            await self.client.is_user_authorized()
        )  # try to auth via initial session file
        if not auth_success:
            # try to auth via telegram desktop
            print(f"First run. Sending code request to Telegram Account {self.phone}")
            # user_phone = input("Enter your phone: ")
            await self.client.sign_in(self.phone)
            self_user = None
            while self_user is None:
                code = input("Enter the code you just received: ")
                self_user = await self.client.sign_in(code=code)
            auth_success = await self.client.is_user_authorized()
        me = await self.client.get_me()
        print(f"Logged in as {me.phone} ({me.id})")
        return auth_success

    async def __a_start_bot(self, bot_username, param):
        bot = await self.client.get_entity(bot_username)
        result = await self.client(
            functions.messages.StartBotRequest(
                bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
                peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
                start_param=param,
            )
        )
        result_data = json.loads(result.to_json())

    async def __a_get_bot_webapp(self, bot_username, platform, url, param):
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

    def login(self):
        self.client.loop.run_until_complete(self.__a_login())

    def start_bot(self, bot_username, param="start"):
        self.client.loop.run_until_complete(self.__a_start_bot(bot_username, param))

    def get_bot_webapp(
        self, bot_username: str, platform: str, url: str, param = None
    ):
        res = self.client.loop.run_until_complete(
            self.__a_get_bot_webapp(bot_username, platform, url, param)
        )
        code.interact(local=locals())
        return res


if __name__ == "__main__":
    akks = localsettings.akks
    choosen_akk = localsettings.current_akk
    api_id = akks[choosen_akk][0]
    api_hash = akks[choosen_akk][1]
    session_id = "ZhokirZhokirych"
    # 07196708-zone-custom-region-ZA-sessid-AxU8Dq0u-sessTime-120:6pGOVG0G@f.proxys5.net:6200
    proxy = {
             'proxy_type': socks.SOCKS5, # (mandatory) protocol to use (see above)
             'addr': 'f.proxys5.net',      # (mandatory) proxy IP address
             'port': 6200,           # (mandatory) proxy port number
             'username': '07196708-zone-custom-region-KW-sessid-lhshTjz2-sessTime-120',      # (optional) username if the proxy requires auth
             'password': '6pGOVG0G',      # (optional) password if the proxy requires auth
             'rdns': True            # (optional) whether to use remote or local resolve, default remote
        }
    tg = Telega(api_id=api_id, api_hash=api_hash, session_id=session_id, phone='66980282450', proxy=proxy)
    # tg.start_bot("notpx_bot")
    # tg.get_bot_webapp(
    #     bot_username="Binance_Moonbix_bot",
    #     url="https://www.binance.com/en/game/tg/moon-bix",
    #     platform="android",
    # )
    print(
        tg.get_bot_webapp(
            bot_username="notpixel",
            url="https://notpx.app",
            platform="android",
        )
    )

import asyncio
import random
import aiohttp

import notpixel_actions
import notpixel_tools
import settings
from dbutils import TDB
from exceptions import *
from fucktory import Fucktory
from telegram_utils import Telega

proxy = "07196708-zone-custom-region-CA-sessid-C9p85mlF-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
    "https://" + proxy
)

# proxy_host = None


async def main_test_not_pixel():

    url = "https://app.notpx.app/#tgWebAppData=user%3D%257B%2522id%2522%253A726551560%252C%2522first_name%2522%253A%2522A%2522%252C%2522last_name%2522%253A%2522S%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%257D%26chat_instance%3D-7507039722228485151%26chat_type%3Dsender%26auth_date%3D1730547486%26hash%3D740f442384e6ee7987e66a46a2e992b0705ce2ab6840381e970376e9987129a4&tgWebAppVersion=7.10&tgWebAppPlatform=tdesktop&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    db_path = settings.db_path
    db = TDB(dbpath=db_path)

    pa = notpixel_actions.PixelActions(
        url,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        gui_browser_worker_type=None,
        session_id="27642042550",
        db=db,
    )
    # task = (
    #     (80, 80, (255, 141, 161)),
    #     # (80, 81, (255, 141, 161)),
    # )
    await pa.emulate_app_start()
    # templates = await pa.get_templates()
    # template_id = random.choice(list(templates))
    # template_ids = [
    #     "799818229",
    #     "6476501580",
    #     "1325258259",
    #     "6432133792",
    #     "1353629816",
    #     "153665413",
    #     "1307361893",
    #     "1502904019",
    #     "1675295056",
    #     "1311866928",
    #     "482706122",
    #     "1805262074",
    # ]
    # for _id in template_ids:
    #     good_pixel_colors = await pa.get_template_colors(_id)
    info = await pa.get_account_state()
    pass
    # await pa.run(task)
    # templates = await pa.get_templates()
    # await pa.get_template_colors(917981974)
    # await pa.select_template(917981974)

    # await pa.get_ws_token()

    # await pa.run(task)


async def main_test_telegram():
    acc = "27641279262"
    from telethon import functions, types

    t = Telega(
        telegram_cache_dir=settings.sessions_dir,
        session_id=acc,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
    )

    await t.init_client_tdata(
        tdata_path=f"tdatas/{acc}/tdata",
        platform="windows",
        hardware_id=acc,
        password="f27641279262",
    )

    await t.client.PrintSessions()

    # result = await t.client(functions.account.GetAuthorizationsRequest())
    # print(result.stringify())
    # new_tdesk = await t.client.ToTDesktop(password="86nmsyckk9rlsg")
    # new_tdesk.SaveTData(f"tdatas/{acc}_new/tdata")
    # result = await t.client(functions.auth.ResetAuthorizationsRequest())
    # await t.client.PrintSessions()

    # await t.set_2fa()
    # await t.check_auth()
    # await t.test()

    # await t.start_bot(bot_username="notpx_bot")
    pass


async def main_test_api_telegram():
    t = Telega(
        telegram_cache_dir="tdatas/not_pixel",
        session_id="pixel_ads",
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
    )
    await t.init_client_api(
        api_id="24559526",
        api_hash="b3b683347bfb4709793511c90bce1ec9",
        phone="79146662650",
    )
    # dialogs = await t.client.get_dialogs()
    # for d in dialogs:
    #     print(d.id)
    await t.get_bot_webapp("notpx_bot", "android")
    pass


async def test_proxy():
    if proxy_host:
        await notpixel_tools.ipinfo(proxy_host, proxy_port, proxy_user, proxy_password)


async def test_db():
    import datetime

    db_path = settings.db_path
    db = TDB(dbpath=db_path)
    await db.drop_tables()
    await db.init_schema()
    await db.get_tables()
    await db.add_user(
        number="959672376648",
        tdata_path="tdatas/959672376648/tdata",
        password="Password123",
        proxy="07196708-zone-custom-region-CA-city-ottawa-sessid-Qoeuiuja-sessTime-120:6pGOVG0G@f.proxys5.net:6200",
        startparam="f726551560",
    )
    # users = await db.get_users()
    # await db.set_user_index_update_time(
    # "27642042550", datetime.datetime.now(datetime.UTC)
    # )
    # index_update = await db.get_user_index_update_time("27642042550")
    # dt = datetime.datetime.fromisoformat(index_update)
    # print(index_update)
    pass


async def add_users_to_db():
    import json

    db_path = settings.db_path
    db = TDB(dbpath=db_path)
    # await db.drop_tables()
    # await db.init_schema()
    await db.get_tables()

    with open("server_accs_filled.json", "r") as f:
        data = f.read()
        user_data = json.loads(data)
        for user in user_data:
            await db.add_user(
                number=user_data[user].get("number"),
                tdata_path=user_data[user].get("tdata"),
                password=user_data[user].get("password"),
                proxy=user_data[user].get("proxy"),
            )
    users = await db.get_users()
    pass


async def change_proxy_for_accs():
    proxy_file = "proxy_toronto.txt"
    accs = """27843070393
27843030175
27840995072
27681141997
27842476054
27842864138
15197048685
27842854968"""
    accs = accs.split("\n")
    db_path = settings.db_path
    db = TDB(dbpath=db_path)

    for number in accs:
        number = number.strip()
        with open(proxy_file) as f:
            proxy_data = f.read()
            proxies = proxy_data.strip().split("\n")
            proxy = proxies.pop(-1)
        with open(proxy_file, "w") as f:
            f.write("\n".join(proxies))
        await db.set_user_proxy(proxy)


async def fill_server_accs_proxy():
    import json
    import random

    server_accs = "server_accs.json"
    proxy_file = "proxies"
    with open(server_accs, "r") as f:
        acc_data = f.read()
        acc_data = json.loads(acc_data)
    with open(proxy_file, "r") as f:
        proxies = f.read()
        proxies = proxies.split("\n")
        random.shuffle(proxies)
    for acc_number in acc_data:
        proxy = proxies.pop()
        if not acc_data[acc_number].get("proxy"):
            acc_data[acc_number]["proxy"] = proxy

    with open("server_accs_filled.json", "w") as f:
        f.write(json.dumps(acc_data))


async def test_http_part_read():
    from notpixel_tools import http_request
    import datetime

    dt_now = datetime.datetime.now(datetime.UTC)
    dt_since = dt_now - datetime.timedelta(minutes=30)
    time_since = dt_since.strftime("%a, %d %b %Y %H:%M:%S GMT")
    proxy_string = "http://127.0.0.1:8080"
    ans = await http_request(
        "GET",  # GET|POST
        "https://app.notpx.app/assets/index-DVD8V7Pc.js",
        {"User-Agent": "chrome", "If-Modified-Since": time_since},
        proxy=proxy_string,
        http_timeout=30,
        good_statuses=[200, 304],
        logger=None,
        retry_count=1,
    )
    pass


# TODO разделить при инициализации фабрики аккаунты на OLD и NEW по наличию или отсутствию успешних ранов раньше
# init accounts fail- first - change proxy, second - remove session - then - exception

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    # loop.run_until_complete(test_proxy())
    # loop.run_until_complete(main_test_not_pixel())
    # loop.run_until_complete(main_test_telegram())
    # loop.run_until_complete(main_test_api_telegram())
    loop.run_until_complete(test_db())
    # loop.run_until_complete(main_test_fucktory())
    # loop.run_until_complete(test_websocket())
    # loop.run_until_complete(fill_server_accs_proxy())
    # loop.create_task(add_users_to_db())
    # loop.create_task(add_users_to_db())
    # loop.run_until_complete(add_users_to_db())
    # loop.run_until_complete(add_downloaded_accs())

    loop.run_until_complete(test_http_part_read())
    # REFERALL TECHNICS
    loop.close()
    print("Finish")

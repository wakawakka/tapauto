from timeout_decorator import timeout

import notpixel_actions
import notpixel_tools
from exceptions import *
from telegram_utils import Telega
from fucktory import Fucktory

import asyncio

proxy = "07196708-zone-custom-region-CA-city-vancouver-sessid-m5G27rH0-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
    "https://" + proxy
)


async def main_test_not_pixel():

    url = "https://app.notpx.app/#tgWebAppData=user%3D%257B%2522id%2522%253A726551560%252C%2522first_name%2522%253A%2522A%2522%252C%2522last_name%2522%253A%2522S%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%257D%26chat_instance%3D-7507039722228485151%26chat_type%3Dsender%26auth_date%3D1728482016%26hash%3D689ef6478a97ea5ed00ce4c8d3027b496ff697dc17e82f8469b15fb1cdef797b&tgWebAppVersion=7.10&tgWebAppPlatform=tdesktop&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    pa = notpixel_actions.PixelActions(
        url,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        gui_browser_worker_type=None,
    )
    task = (
        (80, 80, (255, 141, 161)),
        (80, 81, (255, 141, 161)),
        (81, 80, (255, 141, 161)),
        (81, 81, (255, 141, 161)),
    )
    await pa.run(task)


async def main_test_telegram():

    t = Telega(
        telegram_cache_dir="tdatas/bebe2",
        session_id="27620745705",
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
    )

    await t.init_client_tdata(
        tdata_path="tdatas/16049015240/tdata",
        platform="macos",
        hardware_id="16049015240",
        password="Reza1357",
    )
    await t.start_bot(bot_username="notpx_bot")
    pass


async def main_test_fucktory():
    picture_path = "./notpixel_settings/228.png"
    slaves_path = "slaves_mac.json"

    fk = Fucktory(picture_path, (228, 228))
    # code.interact(local=locals())
    # some logic on how much workers needed for task
    await fk.initial_get_workers(slaves_path)
    # some logic on parallel/non parallel run of the job
    await fk.run_async(catch=False)
    # asyncio.run(fk.do_stuff_periodically_async(10, fk.run_async))
    pass


async def test_proxy():
    await notpixel_tools.ipinfo(proxy_host, proxy_port, proxy_user, proxy_password)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_proxy())
    # loop.run_until_complete(main_test_telegram())
    # loop.run_until_complete(main_test_fucktory())

    loop.close()
    print("Finish")

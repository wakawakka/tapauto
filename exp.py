from timeout_decorator import timeout

import notpixel_actions
import notpixel_tools
from exceptions import *
from telegram_utils import Telega

import asyncio


async def main_test_not_pixel():
    proxy = "07196708-zone-custom-region-CA-sessid-6djuNqVP-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    proxy_host = None

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
    proxy = "07196708-zone-custom-region-CA-sessid-6djuNqVP-sessTime-120:6pGOVG0G@f.proxys5.net:6200"
    proxy_host, proxy_port, proxy_user, proxy_password = notpixel_tools.parse_proxy_url(
        "https://" + proxy
    )
    proxy_host = None

    t = Telega(
        telegram_cache_dir="tdatas/bebe2",
        session_id="228",
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
        logfile_path="common.log",
        logging_level=logging.DEBUG,
    )

    await t.init_client_tdata(
        tdata_path="tdatas/bebe2/tdata",
        platform="desktop",
        hardware_id="228",
        password="Reza1357",
    )
    pass


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_test_telegram())
    loop.close()
    print("Finish")

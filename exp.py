import secure_browser
from telegram_utils import Telega
import settings
import localsettings

if __name__ == "__main__":
    akks = localsettings.akks
    choosen_akk = localsettings.current_akk
    api_id = "24559526"
    api_hash = "b3b683347bfb4709793511c90bce1ec9"
    phone = "89146662650"
    session_id = "228"
    # 07196708-zone-custom-region-ZA-sessid-AxU8Dq0u-sessTime-120:6pGOVG0G@f.proxys5.net:6200

    proxy = False
    proxy_host = "f.proxys5.net"
    proxy_port = 6200
    proxy_user = (
        "07196708-zone-custom-region-CA-city-toronto-sessid-lAVEyUMz-sessTime-120"
    )
    proxy_password = "6pGOVG0G"

    tg = Telega(
        session_id="228",
        telegram_cache_dir=settings.telegram_cache,
        proxy=proxy,
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_user=proxy_user,
        proxy_password=proxy_password,
    )
    # tg.start_bot("notpx_bot")
    # tg.get_bot_webapp(
    #     bot_username="Binance_Moonbix_bot",
    #     url="https://www.binance.com/en/game/tg/moon-bix",
    #     platform="android",
    # )
    tg.init_client_api(api_id=api_id, api_hash=api_hash, phone=phone)
    url = tg.get_bot_webapp(
        bot_username="notpixel",
        url="https://notpx.app",
        platform="android",
    )
    print(f"Got url {url}")
    browser = secure_browser.Browser()

    correct_url = "https://app.notpx.app/#tgWebAppData=user%3D%257B%2522id%2522%253A6444194100%252C%2522first_name%2522%253A%2522Not%2522%252C%2522last_name%2522%253A%2522Pixel%2520Ads%2522%252C%2522username%2522%253A%2522npxad%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26chat_instance%3D4069628147610715339%26chat_type%3Dsender%26auth_date%3D1728053318%26hash%3D072ea79e73d96073642bcec4440f239da2e538beac435bac8a015c70677a890f&tgWebAppVersion=7.10&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22accent_text_color%22%3A%22%23168acd%22%2C%22bg_color%22%3A%22%23ffffff%22%2C%22bottom_bar_bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%2340a7e3%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22destructive_text_color%22%3A%22%23d14e4e%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23999999%22%2C%22link_color%22%3A%22%23168acd%22%2C%22secondary_bg_color%22%3A%22%23f1f1f1%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23168acd%22%2C%22section_separator_color%22%3A%22%23e7e7e7%22%2C%22subtitle_text_color%22%3A%22%23999999%22%2C%22text_color%22%3A%22%23000000%22%7D"

    browser.browser.get(correct_url)
    pass

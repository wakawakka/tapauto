from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions, types

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions


import detector

from hashlib import md5
import time
import random
import io

import os
import localsettings

akks = localsettings.akks
choosen_akk = localsettings.current_akk


# Your API ID and API Hash obtained from my.telegram.org
api_id = akks[choosen_akk][0]  # Example: 123456
api_hash = akks[choosen_akk][1]  # Example: 'abcdef1234567890abcdef1234567890'


bot_username = "Binance_Moonbix_bot"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

# Optional: You can store the session as a string or a file (for reusing sessions).
# Use StringSession or just the filename for a file session.
session_file = choosen_akk  # Session file will be created (anon.session)
client = TelegramClient(session_file, api_id, api_hash)


async def __get_moonbix_url():
    # Check if the session file exists, otherwise prompt for phone number
    if not os.path.exists(f"{session_file}.session"):
        print("Session not found, starting new session...")

        # Initiating login flow
        await client.start()

        # Save the session string to reuse it next time
        session_string = StringSession.save(client.session)
        print(f"Your session string: {session_string}")
    else:
        print("Session found, logging in...")

    # After logging in, print your information
    me = await client.get_me()
    print(f"Logged in as {me.first_name} ({me.id})")

    bot = await client.get_entity(bot_username)

    # start bot here

    dialog = None
    async for dialog in client.iter_dialogs():
        try:
            dialog_user = dialog.entity.username
            if dialog_user == bot_username:
                break
        except:
            continue

    if dialog.entity.username == bot_username:
        print(f"Found bot: {dialog.entity.username} - {dialog.name}")

    bot = await client.get_entity(bot_username)
    result = await client(
        functions.messages.RequestWebViewRequest(
            bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
            peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
            platform="tdesktop",
            from_bot_menu="YES",
            url="https://www.binance.com/game/tg/moon-bix",
        )
    )
    # TODO ADD PARAMS OF RENDER

    return result.url


def get_moonbix_login_url():
    with client:
        q = client.loop.run_until_complete(__get_moonbix_url())
    print(f"Got app url: {q}")
    return q


url = get_moonbix_login_url()
options = ChromeOptions()
options.add_argument(f"--user-agent={user_agent}")
browser = uc.Chrome(headless=False, options=options)


class Moonbix:
    def __init__(self, browser):
        self.browser = browser
        browser.set_window_size(390, 844)

    def sleep(self):
        time.sleep(random.uniform(0.5, 2))

    def small_sleep(self):
        time.sleep(random.uniform(0.1, 0.2))

    def scroll_and_click(self, element):
        action = ActionChains(self.browser, duration=500)
        action.scroll_to_element(element)
        action.move_to_element_with_offset(
            element, random.randint(-2, 2), random.randint(-2, 2)
        )
        action.click()
        action.perform()

    def input_text(self, element, text):
        self.scroll_and_click(element)
        for key in text:
            element.send_keys(key)
            self.small_sleep()
        self.sleep()

    def find_element(self, By_what, By_value, many=False, delay=10):
        t = time.time()
        if many:
            find_fn = self.browser.find_elements
        else:
            find_fn = self.browser.find_element
        while time.time() < t + delay:
            try:
                search_obj = find_fn(By_what, By_value)
                if search_obj:
                    return search_obj
            except:
                time.sleep(0.2)


mb = Moonbix(browser)
mb.browser.get(url)
mb.sleep()
cookie_reject_button = mb.find_element(
    By.XPATH, '//button[contains(text(), "Reject Additional Cookies")]', False
)
mb.scroll_and_click(cookie_reject_button)
mb.sleep()
play_button = mb.find_element(By.XPATH, '//div[contains(text(), "Play Game")]')
mb.scroll_and_click(play_button)

mb.sleep()
canvas = mb.find_element(By.XPATH, "//div/div/div/canvas")
# mb.scroll_and_click(canvas)

d = detector.Detector()
frame_i = 0

while True:
    png = canvas.screenshot_as_png
    hash = md5(png).hexdigest()
    png_io = io.BytesIO(png)
    png_io.seek(0)

    # keep_old_asteroids - economy of calculations of asteroids positions
    # is_shot = d.is_shot(png_io, keep_old_asteroids=False)
    if frame_i % 5 == 0:
        is_shot = d.is_shot(png_io, keep_old_asteroids=False)
    else:
        is_shot = d.is_shot(png_io, keep_old_asteroids=True)
    if is_shot:
        canvas.click()
    # time.sleep(0.1)
    frame_i += 1


pass

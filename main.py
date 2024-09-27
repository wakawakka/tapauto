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
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
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
    # result = await client(
    #     functions.messages.RequestWebViewRequest(
    #         # bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
    #         app = types.
    #         peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
    #         platform="tdesktop",
    #         from_bot_menu="YES",
    #         url="https://www.binance.com/game/tg/moon-bix",
    #     )
    # )
    # functions.messages.RequestAppWebViewRequest()
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
options.add_argument("--disable-features=UserAgentClientHint")
options.add_argument("--lang=en-GB")
options.add_argument("--window-size=422,650")
browser = uc.Chrome(
    headless=False,
    options=options,
)


class Moonbix:
    def __init__(self, browser):
        self.browser = browser
        browser.set_window_size(344, 650)

        webGL = ["Apple Inc.", "Apple GPU", "WebGL 2.0", "WebGL GLSL ES 3.00"]
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
        (function() {
            const webGLRenderer = '"""
                + webGL[0]
                + """';
            const webGLVendor = '"""
                + webGL[1]
                + """';
            const webGLVersion = '"""
                + webGL[2]
                + """';
            const webGLShadingLanguageVersion = '"""
                + webGL[3]
                + """';

            // Store the original method
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;

            // Override the method for WebGL1
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) { // UNMASKED_RENDERER_WEBGL
                    return webGLRenderer;
                } 
                if (parameter === 37446) { // UNMASKED_VENDOR_WEBGL
                    return webGLVendor;
                }
                if (parameter === 7938) { // GL_VERSION
                    return webGLVersion;
                }
                if (parameter === 35724) { // GL_SHADING_LANGUAGE_VERSION
                    return webGLShadingLanguageVersion;
                }
                return originalGetParameter.call(this, parameter);
            };

            // Override the method for WebGL2 if applicable
            if (typeof WebGL2RenderingContext !== 'undefined') {
                const originalGetParameterWebGL2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return webGLRenderer;
                    }
                    if (parameter === 37446) {
                        return webGLVendor;
                    }
                    if (parameter === 7938) { // GL_VERSION
                        return webGLVersion;
                    }
                    if (parameter === 35724) { // GL_SHADING_LANGUAGE_VERSION
                        return webGLShadingLanguageVersion;
                    }
                    return originalGetParameterWebGL2.call(this, parameter);
                };
            }
        })();
        """
            },
        )
        browser.execute_cdp_cmd("Network.enable", {})
        browser.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": user_agent,  # Set your custom User-Agent
                "acceptLanguage": "en-GB,en;q=0.9",  # You can also override Accept-Language
                "platform": "MacIntel",  # Optional platform
                "userAgentMetadata": {  # Set `userAgentMetadata` to avoid sending `Sec-CH-UA` hints
                    "brands": [],  # Remove Sec-CH-UA by providing empty brands
                    "platform": "",  # Remove Sec-CH-UA-Platform
                    "platformVersion": "",  # Empty version
                    "architecture": "",  # Remove Sec-CH-UA-Arch
                    "model": "",  # Remove model (if necessary)
                    "mobile": False,  # Whether it's a mobile device
                },
            },
        )
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            // Disable navigator.userAgentData (Client Hints)
            Object.defineProperty(navigator, 'userAgentData', {
                get: function() {
                    return undefined; // Disable by returning undefined
                }
            });

            // Modify navigator properties
            Object.defineProperty(navigator, 'vendor', {
                get: function() {
                    return 'Apple Computer, Inc.'; // Change to desired vendor
                }
            });

            Object.defineProperty(navigator, 'userAgent', {
                get: function() {
                    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)'; // Set your custom userAgent
                }
            });

            Object.defineProperty(navigator, 'appVersion', {
                get: function() {
                    return '5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)'; // Set your custom appVersion
                }
            });

            Object.defineProperty(navigator, 'product', {
                get: function() {
                    return 'Gecko'; // Set custom product
                }
            });

            Object.defineProperty(navigator, 'productSub', {
                get: function() {
                    return '20030107'; // Set custom productSub
                }
            });

            Object.defineProperty(navigator, 'appName', {
                get: function() {
                    return 'Netscape'; // Set custom appName
                }
            });

            Object.defineProperty(navigator, 'appCodeName', {
                get: function() {
                    return 'Mozilla'; // Set custom appCodeName
                }
            });
        """
            },
        )
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            // Disable Battery Status API
            Object.defineProperty(navigator, 'getBattery', {
                get: function() {
                    return undefined; // Disable Battery API by returning undefined
                }
            });

            // Disable Network Information API
            Object.defineProperty(navigator, 'connection', {
                get: function() {
                    return undefined; // Disable Network Information API by returning undefined
                }
            });

            // Disable Web Bluetooth API
            Object.defineProperty(navigator, 'bluetooth', {
                get: function() {
                    return undefined; // Disable Web Bluetooth API by returning undefined
                }
            });

            // If you want to modify specific properties within these APIs, you can do so like this:
            // For Battery API (returning specific values)
            navigator.getBattery = function() {
                return Promise.resolve({
                    charging: false,
                    chargingTime: Infinity,
                    dischargingTime: Infinity,
                    level: 1  // Always full
                });
            };

            // For Network Information API (returning custom values)
            navigator.connection = {
                effectiveType: 'unknown',
                downlink: 0,
                rtt: 0,
                saveData: true
            };

            // For Web Bluetooth API (returning custom values)
            navigator.bluetooth = {
                getAvailability: function() {
                    return Promise.resolve(false);  // Bluetooth not available
                }
            };
        """
            },
        )
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            // Override screen resolution and color depth

            // Define orientation properties
            Object.defineProperty(screen.orientation, 'type', {get: function() { return 'landscape-primary'; }});
            Object.defineProperty(screen.orientation, 'angle', {get: function() { return 0; }});

            // Override window properties
            Object.defineProperty(window, 'innerWidth', {get: function() { return 422; }});
            Object.defineProperty(window, 'innerHeight', {get: function() { return 650; }});
            Object.defineProperty(window, 'outerWidth', {get: function() { return 0; }});
            Object.defineProperty(window, 'outerHeight', {get: function() { return 0; }});
            Object.defineProperty(window, 'devicePixelRatio', {get: function() { return 2; }});

            // Handle clientWidth and clientHeight for divs
            HTMLElement.prototype.clientWidth = 407;
            HTMLElement.prototype.clientHeight = 650;
        """
            },
        )

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
# mb.browser.get(url)


mb.browser.get("https://browserleaks.com/webgl")
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

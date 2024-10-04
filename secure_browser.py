import time
import os
import random
import zipfile

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

import secure_browser_js as sbjs

# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
user_agent = "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36"
app_version = "5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36"

navigator_vendor = "Google Inc."
navigator_product = "Gecko"
navigator_productSub = "20030107"
navigator_appName = "Netscape"
navigator_appCodeName = "Mozilla"

webGL = {
    "webGLRenderer": "Android Emulator OpenGL ES Translator (Apple M1 Pro)",
    "webGLVendor": "Google (Apple)",
    "webGLVersion": "WebGL 2.0 (OpenGL ES 3.0 Chromium)",
    "webGLShadingLanguageVersion": "WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)",
}


class Browser:
    def __init__(
        self,
        proxy: bool = False,
        proxy_host: str = "",
        proxy_port: int = 0,
        proxy_user: str = "",
        proxy_password: str = "",
        profile="",
        save_browser_profile=False,
    ):
        options = ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-features=UserAgentClientHint")
        options.add_argument("--lang=en")

        if proxy:
            PROXY_FOLDER_ROOT = os.path.join(os.getcwd(), profile, "extensions")
            PROXY_FOLDER = os.path.join(PROXY_FOLDER_ROOT, "proxy_chrome")

            if not os.path.exists(PROXY_FOLDER):
                os.makedirs(PROXY_FOLDER)

            with open(f"{PROXY_FOLDER}/manifest.json", "w") as f:
                f.write(sbjs.chrome_proxy_manifest_json)
            with open(f"{PROXY_FOLDER}/background.js", "w") as f:
                f.write(
                    sbjs.generate_chrome_proxy_background_js(
                        proxy_host, proxy_port, proxy_user, proxy_password
                    )
                )
            pluginfile = f"{PROXY_FOLDER}/proxy_auth_plugin.zip"

            with zipfile.ZipFile(pluginfile, "w") as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)

            # options.add_argument(f"--load-extension={os.path.join(PROXY_FOLDER_ROOT, 'extensions', 'webrtc')},{PROXY_FOLDER}")
            options.add_argument(f"--load-extension={PROXY_FOLDER}")
        self.browser = uc.Chrome(
            headless=False,
            options=options,
        )

        self.browser.set_window_size(700, 900)

        # set_device_metrics_override = {
        #     "width": 400,
        #     "height": 700,
        #     "deviceScaleFactor": 20,
        #     "mobile": True,
        # }
        # self.browser.execute_cdp_cmd(
        #     "Emulation.setDeviceMetricsOverride", set_device_metrics_override
        # )

        self.browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": sbjs.generate_webgl_poof_js(webGL)},
        )
        self.browser.execute_cdp_cmd("Network.enable", {})
        self.browser.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": user_agent,  # Set your custom User-Agent
                "acceptLanguage": "en-GB,en;q=0.9",  # You can also override Accept-Language
                "platform": "Linux aarch64",  # Correct platform for Android
                "userAgentMetadata": {
                    "brands": [
                        {"brand": "Not-A;Brand", "version": "99"},
                        {"brand": "Chromium", "version": "115"},
                        {"brand": "Google Chrome", "version": "115"},
                    ],  # Mimic Sec-CH-UA with valid brand versions
                    "fullVersionList": [
                        {"brand": "Not-A;Brand", "version": "99.0.0.0"},
                        {"brand": "Chromium", "version": "115.0.0.0"},
                        {"brand": "Google Chrome", "version": "115.0.0.0"},
                    ],
                    "platform": "Android",  # Correct platform for Android
                    "platformVersion": "10.0",  # Provide an actual platform version for Android
                    "architecture": "arm64",  # Typical Android architecture
                    "model": "Pixel 5",  # Set a model if needed
                    "mobile": True,  # True for mobile devices
                },
            },
        )
        self.browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": sbjs.generate_navigator_replaces(
                    navigator_vendor,
                    user_agent,
                    app_version,
                    navigator_product,
                    navigator_productSub,
                    navigator_appName,
                    navigator_appCodeName,
                )
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

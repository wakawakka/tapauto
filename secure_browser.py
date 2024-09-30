import time
import random

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
user_agent = "Mozilla/5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36"
app_version = "5.0 (Linux; Android 13; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.61 Mobile Safari/537.36"

navigator_vendor = "Google Inc."
navigator_product = "Gecko"
navigator_productSub = "20030107"
navigator_appName = "Netscape"
navigator_appCodeName = "Mozilla"

webGL = [
    "Android Emulator OpenGL ES Translator (Apple M1 Pro)",
    "Google (Apple)",
    "WebGL 2.0 (OpenGL ES 3.0 Chromium)",
    "WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)",
]


class Browser:
    def __init__(self):
        options = ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-features=UserAgentClientHint")
        options.add_argument("--lang=en")
        self.browser = uc.Chrome(
            headless=False,
            options=options,
        )
        self.browser.set_window_size(700, 900)

        self.browser.execute_cdp_cmd(
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
        self.browser.execute_cdp_cmd("Network.enable", {})
        self.browser.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": user_agent,  # Set your custom User-Agent
                "acceptLanguage": "en-GB,en;q=0.9",  # You can also override Accept-Language
                "platform": "Linux aarch64",  # Optional platform
                # "userAgentMetadata": {  # Set `userAgentMetadata` to avoid sending `Sec-CH-UA` hints
                #     "brands": [],  # Remove Sec-CH-UA by providing empty brands
                #     "platform": [],  # Remove Sec-CH-UA-Platform
                #     "platformVersion": "",  # Empty version
                #     "architecture": "",  # Remove Sec-CH-UA-Arch
                #     "model": "",  # Remove model (if necessary)
                #     "mobile": False,  # Whether it's a mobile device
                # },
            },
        )
        self.browser.execute_cdp_cmd(
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
                    return '"""
                + navigator_vendor
                + """'; // Change to desired vendor
                }
            });

            Object.defineProperty(navigator, 'userAgent', {
                get: function() {
                    return '"""
                + user_agent
                + """'; // Set your custom userAgent
                }
            });

            Object.defineProperty(navigator, 'appVersion', {
                get: function() {
                    return '"""
                + app_version
                + """'; // Set your custom appVersion
                }
            });

            Object.defineProperty(navigator, 'product', {
                get: function() {
                    return '"""
                + navigator_product
                + """'; // Set custom product
                }
            });

            Object.defineProperty(navigator, 'productSub', {
                get: function() {
                    return '"""
                + navigator_productSub
                + """'; // Set custom productSub
                }
            });

            Object.defineProperty(navigator, 'appName', {
                get: function() {
                    return '"""
                + navigator_appName
                + """'; // Set custom appName
                }
            });

            Object.defineProperty(navigator, 'appCodeName', {
                get: function() {
                    return '"""
                + navigator_appCodeName
                + """'; // Set custom appCodeName
                }
            });
        """
            },
        )
        self.browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            Object.defineProperty(navigator, 'languages', {
                get: function() { return ['en', 'en-US']; }
            });
            Object.defineProperty(navigator, 'maxTouchPoints', {
                get: function() { return 1; }
            });"""
                + """// Disable Battery Status API
            Object.defineProperty(navigator, 'getBattery', {
                get: function() {
                    return undefined; // Disable Battery API by returning undefined
                }
            });"""
                * 0
                + """// Disable Network Information API
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

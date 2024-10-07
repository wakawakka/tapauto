chrome_proxy_manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

firefox_proxy_manifest_json = """
{
  "name": "My Firefox Proxy",
  "version": "1.0.0b",
  "manifest_version": 2,
  "permissions": [
    "browsingData",
    "proxy",
    "storage",
    "tabs",
    "webRequest",
    "webRequestBlocking",
    "downloads",
    "notifications",
    "<all_urls>"
  ],
  "background": {
    "scripts": ["background.js"]
  },
  "browser_specific_settings": {
    "gecko": {
      "id": "myproxy@example.org"
    }
  }
}
"""


def generate_chrome_proxy_background_js(
    proxy_host, proxy_port, proxy_user, proxy_password
):
    background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (
        proxy_host,
        proxy_port,
        proxy_user,
        proxy_password,
    )
    return background_js


def generate_firefox_proxy_background_js(
    proxy_host, proxy_port, proxy_user, proxy_password
):
    background_js = """
// Proxy credentials
const PROXY_HOST = "%s";
const PROXY_PORT = "%s";
const PROXY_USERNAME = "%s";
const PROXY_PASSWORD = "%s";

var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: PROXY_HOST,
        port: PROXY_PORT
      },
      bypassList: []
    }
 };


function proxyRequest(request_data) {
    return {
        type: "http",
        host: PROXY_HOST, 
        port: PROXY_PORT
    };
}

browser.proxy.settings.set({value: config, scope: "regular"}, function() {;});

function callbackFn(details) {
return {
    authCredentials: {
        username: PROXY_USERNAME,
        password: PROXY_PASSWORD
    }
};
}

browser.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);

browser.proxy.onRequest.addListener(proxyRequest, {urls: ["<all_urls>"]});
""" % (
        proxy_host,
        proxy_port,
        proxy_user,
        proxy_password,
    )
    return background_js


def generate_webgl_poof_js(webGL):
    render = webGL["webGLRenderer"]
    vendor = webGL["webGLVendor"]
    version = webGL["webGLVersion"]
    shading = webGL["webGLShadingLanguageVersion"]

    js = """
(function() {
    const webGLRenderer = '%s';
    const webGLVendor = '%s';
    const webGLVersion = '%s';
    const webGLShadingLanguageVersion = '%s';

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
""" % (
        render,
        vendor,
        version,
        shading,
    )
    return js


def generate_navigator_replaces(
    navigator_vendor,
    user_agent,
    app_version,
    navigator_product,
    navigator_productSub,
    navigator_appName,
    navigator_appCodeName,
):
    nav_js = """
// Disable navigator.userAgentData (Client Hints)
Object.defineProperty(navigator, 'userAgentData', {
    get: function() {
        return undefined; // Disable by returning undefined
    }
});

// Modify navigator properties
Object.defineProperty(navigator, 'vendor', {
    get: function() {
        return '%s'; // Change to desired vendor
    }
});

Object.defineProperty(navigator, 'userAgent', {
    get: function() {
        return '%s'; // Set your custom userAgent
    }
});

Object.defineProperty(navigator, 'appVersion', {
    get: function() {
        return '%s'; // Set your custom appVersion
    }
});

Object.defineProperty(navigator, 'product', {
    get: function() {
        return '%s'; // Set custom product
    }
});

Object.defineProperty(navigator, 'productSub', {
    get: function() {
        return '%s'; // Set custom productSub
    }
});

Object.defineProperty(navigator, 'appName', {
    get: function() {
        return '%s'; // Set custom appName
    }
});

Object.defineProperty(navigator, 'appCodeName', {
    get: function() {
        return '%s'; // Set custom appCodeName
    }
});
""" % (
        navigator_vendor,
        user_agent,
        app_version,
        navigator_product,
        navigator_productSub,
        navigator_appName,
        navigator_appCodeName,
    )
    return nav_js

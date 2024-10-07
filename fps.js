const { plugin } = require('puppeteer-with-fingerprints');
plugin.setServiceKey('aFzeGSVZpuER3jVKcR9iKuAkwf9SkavnV9Td6G3XxZJynOzGsFoRPaErD8poUE5y');

(async () => {
  // Get a fingerprint from the server:
  const fingerprint = await plugin.fetch({
    tags: ['Firefox', 'Android'],
  });

  // Apply fingerprint:
  plugin.useFingerprint(fingerprint);
  let proxy = '07196708-zone-custom-region-CA-sessid-Yx66zz1m-sessTime-15:6pGOVG0G@f.proxys5.net:6200';
  /*
  plugin.useProxy(proxy, {
    // Change browser timezone according to proxy:
    changeTimezone: true,
    // Replace browser geolocation according to proxy:
    changeGeolocation: true,
  });
  */

  // Launch the browser instance:
  const browser = await plugin.launch({
    headless: false,
    args: [`--window-size=900,900`],
    defaultViewport: {
      width:900,
      height:900
    }
  });

  // The rest of the code is the same as for a standard `puppeteer` library:
  const page = await browser.newPage();
  await page.setViewport({width: 900, height: 900});
  await page.goto('https://ipinfo.io/json');
})();
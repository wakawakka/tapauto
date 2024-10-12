const { plugin } = require('puppeteer-with-fingerprints');

(async () => {
  // Get a fingerprint from the server:
  const fingerprint = await plugin.fetch('', {
    tags: ['Android', 'Safari'],
  });

  // Apply fingerprint:
  plugin.useFingerprint(fingerprint);

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
  await page.goto('https://example.com');
})();
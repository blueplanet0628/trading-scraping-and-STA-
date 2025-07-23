from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from fixserver import set_popup_browser

popup_browser = None

async def launch_scraper(callback):
    global popup_browser

    LOGIN_ID = 'v9411402'
    PASSWORD = 'skwshjdwyd0330'
    BID_SELECTOR = 'div[uifield="bidPrice"] > div.priceText'
    ASK_SELECTOR = 'div[uifield="askPrice"] > div.priceText'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://demotrade.fx.dmm.com/fxcmdipresen/webrich/direct/login")
        await page.fill('input[name="accountId"]', LOGIN_ID)
        await page.fill('input[name="passwordShow"]', PASSWORD)

        async with context.expect_page() as popup_info:
            await page.click('a.c-btn--login')
        popup = await popup_info.value
        await popup.wait_for_load_state()

        try:
            await popup.wait_for_selector('button#commonMessageClose', timeout=150000)
            await popup.click('button#commonMessageClose')
            popup_browser = popup
            print("[SCRAPER] Popup closed successfully.", popup)
            set_popup_browser(popup_browser)
            print("[SCRAPER] Login successful, popup assigned:", popup_browser)
        except PlaywrightTimeout:
            pass

        await popup.wait_for_selector(BID_SELECTOR, timeout=10000)
        print("[SCRAPER] Logged in and popup ready.")

        while True:
            bid_el = await popup.query_selector(BID_SELECTOR)
            ask_el = await popup.query_selector(ASK_SELECTOR)
            bid = await bid_el.inner_text()
            ask = await ask_el.inner_text()
            callback(bid.strip(), ask.strip())

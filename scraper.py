from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from fixserver import  set_popup_browser  # Import the function to start the FIX server
popup_browser = None  # define global variable outside the function

def launch_scraper(callback):
    global popup_browser  # Declare to assign to the global variable

    LOGIN_ID = 'v9411402'
    PASSWORD = 'skwshjdwyd0330'
    BID_SELECTOR = 'div[uifield="bidPrice"] > div.priceText'
    ASK_SELECTOR = 'div[uifield="askPrice"] > div.priceText'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://demotrade.fx.dmm.com/fxcmdipresen/webrich/direct/login")
        page.fill('input[name="accountId"]', LOGIN_ID)
        page.fill('input[name="passwordShow"]', PASSWORD)

        with context.expect_page() as popup_info:
            page.click('a.c-btn--login')
        popup = popup_info.value
        popup.wait_for_load_state()

        try:
            popup.wait_for_selector('button#commonMessageClose', timeout=150000)
            popup.click('button#commonMessageClose')
            popup_browser = popup  # assign to global variable here
            set_popup_browser(popup_browser)
            print("[SCRAPER] Login successful, popup assigned:", popup_browser)
        except PlaywrightTimeout:
            pass

        popup.wait_for_selector(BID_SELECTOR, timeout=10000)
        print("[SCRAPER] Logged in and popup ready.")


        while True:
            bid = popup.query_selector(BID_SELECTOR).inner_text().strip()
            ask = popup.query_selector(ASK_SELECTOR).inner_text().strip()
            callback(bid, ask)

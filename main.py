# main.py
import socket
import threading
import datetime
import time
import asyncio
import socketserver

from fix_builder import build_new_order
from dmm_api import send_order_to_dmm
from fixserver import set_popup_browser

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 5001
UDP_PORT_RECV = 5002
UDP_PORT_EXEC_REPORT = 5003

seq_num = 1
last_order_time = 0
SOH = '\x01'

popup_browser = None
main_loop = None


def send_fix_udp(message: str, ip=UDP_IP, port=UDP_PORT_SEND):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode('ascii'), (ip, port))
    print("[SENT]", message.replace(SOH, '|'))


def receive_exec_reports():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT_EXEC_REPORT))
    print(f"[LISTEN] Receiving Execution Reports on 0.0.0.0:{UDP_PORT_EXEC_REPORT}")
    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode('ascii')
        print(f"[RECEIVED EXEC REPORT] From {addr}: {msg.replace(SOH, '|')}")


def send_order_to_sta(symbol: str, side: str, qty: int, price: float):
    global seq_num
    cl_ord_id = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d-%H%M%S%f")[:-3]
    fix_msg = build_new_order(seq_num, cl_ord_id, symbol, side, qty, price)
    send_fix_udp(fix_msg)
    seq_num += 1


def handle_bid_ask(bid, ask):
    global last_order_time
    now = time.time()

    bid_float = float(bid)
    ask_float = float(ask)
    spread = ask_float - bid_float

    if spread < 0.003 and (now - last_order_time) >= 10:
        print("[ORDER] Sending order to STA...")
        send_order_to_sta("USDJPY", "1", 1, ask_float)  # 54=1 for Buy
        last_order_time = now


def parse_fix(message):
    return {
        tag: val
        for tag, val in (
            field.split('=', 1)
            for field in message.strip().split(SOH)
            if '=' in field
        )
    }


def build_execution_report(order):
    fields = [
        "8=FIX.4.2", "9=000", "35=8", "34=1", "49=SERVER", "56=CLIENT",
        f"52={order.get('52', '')}",
        f"11={order.get('11', '')}",
        "150=0", "39=0",
        f"55={order.get('55', '')}",
        f"54={order.get('54', '')}",
        f"38={order.get('38', '')}",
        f"44={order.get('44', '')}",
    ]
    body = SOH.join(fields[2:]) + SOH
    fields[1] = f"9={len(body.encode('ascii'))}"
    fix_msg = SOH.join(fields) + SOH
    checksum = sum(fix_msg.encode('ascii')) % 256
    fix_msg += f"10={checksum:03}{SOH}"
    return fix_msg


async def process_order(order, sock, client_addr):
    global popup_browser
    print(f"[STA] Parsed Order: {order}", popup_browser)
    success, err = await send_order_to_dmm(popup_browser, order)

    if not success:
        print(f"[ERROR] Order failed: {err}")

    exec_report = build_execution_report(order)
    try:
        sock.sendto(exec_report.encode('ascii'), client_addr)
        print(f"[STA] Sent Execution Report to {client_addr}")
    except UnicodeEncodeError:
        sock.sendto(exec_report.encode('ascii', errors='ignore'), client_addr)
        print(f"[STA] Sent Execution Report (non-ASCII removed)")


class FIXUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global main_loop
        data = self.request[0].decode('ascii', errors='ignore')
        sock = self.request[1]
        client_addr = self.client_address

        print(f"[STA] Received: {data.replace(SOH, '|')}")
        order = parse_fix(data)

        asyncio.run_coroutine_threadsafe(process_order(order, sock, client_addr), main_loop)


def start_fix_server():
    server = socketserver.UDPServer(("", UDP_PORT_SEND), FIXUDPHandler)  # ✅ use UDP_PORT_SEND (5001)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[FIX SERVER] Listening on UDP {UDP_PORT_SEND}")

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
        # popup_browser = popup
        # set_popup_browser(popup_browser)
        try:
            await popup.wait_for_selector('button#commonMessageClose', timeout=150000)
            await popup.click('button#commonMessageClose')
            popup_browser = popup
            set_popup_browser(popup_browser)
            print("[SCRAPER] Login successful, popup assigned:", popup_browser)
        except PlaywrightTimeout:
            pass

        await popup.wait_for_selector(BID_SELECTOR, timeout=150000)
        print("[SCRAPER] Logged in and popup ready.")

        while True:
            bid_el = await popup.query_selector(BID_SELECTOR)
            ask_el = await popup.query_selector(ASK_SELECTOR)
            bid = await bid_el.inner_text()
            ask = await ask_el.inner_text()
            callback(bid.strip(), ask.strip())


async def main():
    global popup_browser, main_loop

    main_loop = asyncio.get_event_loop()

    threading.Thread(target=receive_exec_reports, daemon=True).start()
    start_fix_server()

    await launch_scraper(handle_bid_ask)


if __name__ == "__main__":
    asyncio.run(main())
import socket
import threading
import datetime
import asyncio
import socketserver
import time         # <--- Add this import


from fix_builder import build_new_order  # Assumed implemented
from dmm_api import send_order_to_dmm    # Async order executor
from fixserver import set_popup_browser  # Shared popup instance setter

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

TCP_IP = "127.0.0.1"
TCP_PORT_LISTEN = 5001        # STA listens for TCP FIX orders here
SOH = '\x01'

seq_num = 1                   # MsgSeqNum for outgoing orders from STA (if any)
exec_seq_num = 1              # MsgSeqNum for Execution Reports

popup_browser = None
main_loop = None
last_order_time = 0


def parse_fix(message):
    return {
        tag: val
        for tag, val in (
            field.split('=', 1)
            for field in message.strip().split(SOH)
            if '=' in field
        )
    }


def build_fix_message(fields):
    body = SOH.join(f"{tag}={value}" for tag, value in fields) + SOH
    body_length = len(body)
    header = f"8=FIX.4.4{SOH}9={body_length}{SOH}"
    msg = header + body
    checksum = sum(ord(c) for c in msg) % 256
    msg += f"10={checksum:03}{SOH}"
    return msg


def build_execution_report(order, seq_num, sender="YOUR_BRIDGE", target="STA"):
    fields = [
        ("35", "8"),              # Execution Report
        ("49", sender),
        ("56", target),
        ("34", str(seq_num)),
        ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
        ("11", order.get("11", "")),
        ("17", f"EXEC{order.get('11', '')}"),
        ("150", order.get("150", "0")),
        ("39", order.get("39", "0")),
        ("55", order.get("55", "")),
        ("54", order.get("54", "")),
        ("38", order.get("38", "")),
        ("44", order.get("44", "")),
    ]
    return build_fix_message(fields)


async def process_order(order, client_socket):
    global popup_browser, exec_seq_num
    print(f"[STA] Processing order: {order}")

    if popup_browser is None:
        print("[ERROR] Popup browser not initialized! Cannot send order to DMM.")
        order["150"] = "8"  # ExecType = Rejected
        order["39"] = "8"   # OrdStatus = Rejected
    else:
        try:
            print(f"[STA] Sending order to DMM: Symbol={order.get('55')}, Side={order.get('54')}, Qty={order.get('38')}, Price={order.get('44')}")
            success, result_or_err = await send_order_to_dmm(popup_browser, order)
        except Exception as e:
            success = False
            result_or_err = f"Exception in send_order_to_dmm: {e}"

        if success:
            print(f"[DMM ORDER] Success: {result_or_err}")
            for k, v in result_or_err.items():
                order[k] = v
            order["150"] = "2"  # ExecType = Filled (or as appropriate)
            order["39"] = "2"   # OrdStatus = Filled
        else:
            print(f"[DMM ORDER] Failed: {result_or_err}")
            order["150"] = "8"  # ExecType = Rejected
            order["39"] = "8"   # OrdStatus = Rejected

    exec_report = build_execution_report(order, exec_seq_num)
    exec_seq_num += 1

    try:
        client_socket.sendall(exec_report.encode('ascii'))
        print("[STA] Sent Execution Report to STA via TCP")
    except Exception as e:
        print(f"[ERROR] Failed to send Execution Report: {e}")


class FIXTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global main_loop
        client_socket = self.request
        client_addr = self.client_address
        print(f"[STA] Client connected: {client_addr}")

        try:
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'10=' in data:  # crude end of FIX message detection
                    break

            message = data.decode('ascii', errors='ignore')
            print(f"[STA] Received FIX message: {message.replace(SOH, '|')}")
            order = parse_fix(message)

            if order.get("35") == "D":
                print("[STA] NewOrderSingle received, processing order...")
                # Schedule order processing asynchronously on the main event loop
                asyncio.run_coroutine_threadsafe(process_order(order, client_socket), main_loop)
            else:
                print(f"[STA] Unsupported FIX message type: {order.get('35')}")

        except Exception as e:
            print(f"[ERROR] FIXTCPHandler exception: {e}")


def start_fix_server():
    server = socketserver.ThreadingTCPServer(("", TCP_PORT_LISTEN), FIXTCPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[FIX SERVER] Listening on TCP port {TCP_PORT_LISTEN}")


def handle_bid_ask(bid, ask):
    global last_order_time
    now = time.time()

    bid_float = float(bid)
    ask_float = float(ask)
    spread = ask_float - bid_float

    if spread < 0.003 and (now - last_order_time) >= 10:
        print("[ORDER] Sending order to STA based on spread condition...")
        send_order_to_sta("USDJPY", "1", 1, ask_float)
        last_order_time = now


def send_order_to_sta(symbol: str, side: str, qty: int, price: float):
    global seq_num
    cl_ord_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S%f")[:-3]
    fix_msg = build_new_order(seq_num, cl_ord_id, symbol, side, qty, price)

    # IMPORTANT FIX:
    # STA is listening on TCP, so send order via TCP, NOT UDP.
    try:
        with socket.create_connection((TCP_IP, TCP_PORT_LISTEN), timeout=5) as sock:
            sock.sendall(fix_msg.encode('ascii'))
            print(f"[SENT TO STA] {fix_msg.replace(SOH, '|')}")
    except Exception as e:
        print(f"[ERROR] Failed to send order to STA TCP server: {e}")

    seq_num += 1


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
            set_popup_browser(popup_browser)
            print("[SCRAPER] Login successful, popup assigned:", popup_browser)
        except PlaywrightTimeout:
            popup_browser = popup
            set_popup_browser(popup_browser)
            print("[SCRAPER] Login successful, popup assigned (no message close needed)")

        await popup.wait_for_selector(BID_SELECTOR, timeout=150000)
        print("[SCRAPER] Popup ready for price updates.")

        while True:
            bid_el = await popup.query_selector(BID_SELECTOR)
            ask_el = await popup.query_selector(ASK_SELECTOR)
            bid = await bid_el.inner_text()
            ask = await ask_el.inner_text()
            callback(bid.strip(), ask.strip())


async def main():
    global popup_browser, main_loop
    main_loop = asyncio.get_event_loop()

    # Start TCP FIX server for incoming orders from STA sender
    start_fix_server()

    # Start Playwright scraper and login
    await launch_scraper(handle_bid_ask)


if __name__ == "__main__":
    asyncio.run(main())

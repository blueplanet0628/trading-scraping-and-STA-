import socket
import threading
import datetime
import time
import asyncio
import socketserver

from fix_builder import build_new_order  # Your helper, assumed implemented
from dmm_api import send_order_to_dmm    # Your async order function
from fixserver import set_popup_browser   # To share popup_browser instance

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 5001        # Receive orders from STA here (UDP)
UDP_PORT_EXEC_REPORT = 5003 # Listen for Execution Reports (optional)
SOH = '\x01'

seq_num = 1                 # MsgSeqNum for sending orders to STA (if needed)
exec_seq_num = 1            # MsgSeqNum for Execution Reports
last_order_time = 0

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
    """
    Build a FIX message string with header, body length, and checksum.
    Returns bytes encoded in ascii.
    """
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
        ("49", sender),           # SenderCompID (server)
        ("56", target),           # TargetCompID (client)
        ("34", str(seq_num)),     # MsgSeqNum
        ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
        ("11", order.get("11", "")),          # ClOrdID
        ("17", f"EXEC{order.get('11', '')}"), # ExecID
        ("150", order.get("150", "0")),       # ExecType
        ("39", order.get("39", "0")),         # OrdStatus
        ("55", order.get("55", "")),          # Symbol
        ("54", order.get("54", "")),          # Side
        ("38", order.get("38", "")),          # OrderQty
        ("44", order.get("44", "")),          # Price
    ]
    return build_fix_message(fields)


async def process_order(order, sock, client_addr):
    global popup_browser, exec_seq_num
    print(f"[STA] Parsed Order: {order}", popup_browser)

    success, exec_result_or_err = await send_order_to_dmm(popup_browser, order)

    # Step 1: Populate order with result data
    if not success:
        print(f"[ERROR] Order failed: {exec_result_or_err}")
        order["150"] = "8"  # ExecType = Rejected
        order["39"] = "8"   # OrdStatus = Rejected
        order["58"] = str(exec_result_or_err)  # Text: Reason
    else:
        print(f"[DMM ORDER] Success: {exec_result_or_err}")
        for k, v in exec_result_or_err.items():
            order[k] = v

        # Set ExecutionReport values if not already set
        order["150"] = "0"  # ExecType = New
        order["39"] = order.get("39", "0")  # OrdStatus = New (default)
        order["17"] = f"EX{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]}"  # ExecID
        order["32"] = order.get("38", "0")  # LastQty
        order["31"] = order.get("44", "0")  # LastPx

    # Step 2: Build Execution Report FIX message
    exec_report = build_execution_report(order, exec_seq_num)
    exec_seq_num += 1

    # Step 3: Send back to STA (via UDP)
    try:
        if isinstance(sock, socket.socket):  # ✅ Check for valid socket
            sock.sendto(exec_report.encode("ascii"), client_addr)
            print(f"[STA] Sent Execution Report to {client_addr}")
        else:
            print(f"[ERROR] Invalid socket object: {sock}")
    except UnicodeEncodeError:
        sock.sendto(exec_report.encode("ascii", errors="ignore"), client_addr)
        print(f"[STA] Sent Execution Report (non-ASCII removed)")
    except Exception as e:
        print(f"[ERROR] Failed to send Execution Report: {e}")




class FIXUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global main_loop
        data = self.request[0].decode('ascii', errors='ignore')
        sock = self.request[1]
        client_addr = self.client_address

        print(f"[STA] Received: {data.replace(SOH, '|')}")
        order = parse_fix(data)

        # Schedule async processing safely on main event loop
        asyncio.run_coroutine_threadsafe(process_order(order, sock, client_addr), main_loop)


def start_fix_server():
    server = socketserver.UDPServer(("", UDP_PORT_SEND), FIXUDPHandler)  # Listen on 5001 UDP
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[FIX SERVER] Listening on UDP {UDP_PORT_SEND}")


def handle_bid_ask(bid, ask):
    global last_order_time
    now = time.time()

    bid_float = float(bid)
    ask_float = float(ask)
    spread = ask_float - bid_float

    if spread < 0.003 and (now - last_order_time) >= 10:
        print("[ORDER] Sending order to STA...")
        # Send a Buy order (54=1)
        send_order_to_sta("USDJPY", "1", 1, ask_float)
        last_order_time = now


def send_order_to_sta(symbol: str, side: str, qty: int, price: float):
    global seq_num
    cl_ord_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S%f")[:-3]
    fix_msg = build_new_order(seq_num, cl_ord_id, symbol, side, qty, price)
    send_fix_udp(fix_msg)
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

    # Start thread to listen for Execution Reports (optional)
    threading.Thread(target=receive_exec_reports, daemon=True).start()

    # Start UDP FIX server
    start_fix_server()

    # Start Playwright scraper (blocking async call)
    await launch_scraper(handle_bid_ask)


if __name__ == "__main__":
    asyncio.run(main())




    >>>>>>>>>>>>>>>>>>>>>>


from playwright.async_api import Page
import asyncio

async def send_order_to_dmm(popup: Page, order: dict) -> tuple[bool, dict | str | None]:
    try:
        # Extract order information
        raw_symbol = order.get("55")  # e.g. 'USDJPY'
        side = order.get("54")        # '1' (Buy) or '2' (Sell)
        order_lot = order.get("38")   # Quantity
        order_id = order.get("11")    # Order ID

        if not raw_symbol or len(raw_symbol) != 6:
            raise ValueError(f"Unexpected or missing symbol format: {raw_symbol}")

        symbol = f"{raw_symbol[:3]}/{raw_symbol[3:]}"
        select_value = f"SPOT_{symbol}"
        print(f"[📡 UI ORDER] symbol='{symbol}' side='{side}' order_lot='{order_lot}' order_id='{order_id}'")

        # --- Select currency pair ---
        dropdown_wrap = popup.locator('span.k-dropdown-wrap').first
        await dropdown_wrap.click()
        option = popup.locator('ul[aria-hidden="false"] li[role="option"]', has_text=symbol)
        await option.wait_for(state='visible', timeout=5000)
        await option.click()
        print(f"[✅ SELECTED SYMBOL] {select_value}")

        # --- Input quantity ---
        input_box = popup.locator('[uifield="orderQuantity"]')
        await input_box.wait_for(state='visible', timeout=5000)
        await input_box.click()
        await input_box.press("Control+A")
        await input_box.press("Backspace")
        await input_box.type(order_lot)
        await input_box.press("Tab")
        print(f"[✅ SET LOT] {order_lot}")

        # --- Click Buy/Sell button ---
        if side == "1":
            await popup.locator('[uifield="bidStreamingButton"]').click()
            print("[✅ CLICKED BUY BUTTON]")
        elif side == "2":
            await popup.locator('[uifield="askStreamingButton"]').click()
            print("[✅ CLICKED SELL BUTTON]")
        else:
            raise ValueError(f"Invalid side value: {side}")

        # --- Confirm order ---
        order_confirm = popup.locator('button[uifield="orderButtonAll"]')
        await order_confirm.wait_for(state="visible", timeout=5000)
        await order_confirm.click()
        print("[✅ CLICKED ORDER CONFIRM BUTTON]")

        # --- Execute order ---
        execute_button = popup.locator('button[uifield="orderExecuteButton"]')
        await execute_button.wait_for(state="visible", timeout=10000)
        for _ in range(10):
            if await execute_button.is_enabled():
                break
            await asyncio.sleep(0.5)
        await execute_button.click()
        print("[✅ CLICKED 一括決済実行ボタン]")

        # --- Close confirmation modal ---
        try:
            await popup.wait_for_selector('#layer p.resultMessage:has-text("注文を受け付けました。")', timeout=7000)
            close_button = popup.locator('#layer button[uifield="closeButton"]', has_text="閉じる")
            await close_button.wait_for(state='visible', timeout=7000)
            await close_button.click()
            print("[✅ 閉じるボタンをクリックしました]")
        except Exception as e:
            print(f"[⚠️ CLOSE WARNING] モーダル閉じる操作失敗: {e}")

        # Prepare execution result on success
        executed_qty = order.get("38")
        executed_price = order.get("44")
        exec_status = "0"  # ExecType '0' = New or filled

        exec_result = {
            "38": executed_qty,
            "44": executed_price,
            "39": exec_status,
            "11": order_id,  # ClOrdID
            "55": raw_symbol,  # Symbol
            "54": side,  # Side
            "result": "order executed successfully",
            # Add other FIX tags if needed
        }
        print('Execution result:', exec_result)

        return True, exec_result

    except Exception as e:
        err_msg = f"{type(e).__name__}: {e}"
        print(f"[❌ ORDER ERROR] {err_msg}")
        # On failure, return False and error message with order info
        return False, {"error": err_msg, "order": order}


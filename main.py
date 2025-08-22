import socket
import threading
import datetime
import socketserver
import time
import asyncio

from fix_builder import build_new_order
from fixserver import set_popup_browser
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SOH = '\x01'
TCP_IP = "127.0.0.1"
PORT_STA_ORDERS = 5001
PORT_STA_EXECUTIONS = 5002

SENDER_COMP_ID = "YOUR_BRIDGE"
TARGET_COMP_ID = "S.T.A."

seq_num = 1
exec_seq_num = 1
execution_clients = []
popup_browser = None
sta_ready = False

def parse_fix(message):
    return {
        tag: val for tag, val in (
            field.split("=", 1) for field in message.strip().split(SOH) if "=" in field
        )
    }

def build_fix_message(fields):
    body = SOH.join(f"{tag}={value}" for tag, value in fields if tag not in ("8", "9", "10")) + SOH
    body_len = len(body)
    header = f"8=FIX.4.4{SOH}9={body_len}{SOH}"
    msg = header + body
    checksum = sum(ord(c) for c in msg) % 256
    msg += f"10={checksum:03}{SOH}"
    return msg

def build_logon_response(seq):
    return build_fix_message([
        ("35", "A"),
        ("34", str(seq)),
        ("49", SENDER_COMP_ID),
        ("56", TARGET_COMP_ID),
        ("98", "0"),
        ("108", "30"),
        ("141", "Y"),
        ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
    ])

def build_execution_report(order, seq):
    return build_fix_message([
        ("35", "8"),
        ("34", str(seq)),
        ("49", SENDER_COMP_ID),
        ("56", TARGET_COMP_ID),
        ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
        ("11", order.get("11", "")),
        ("17", f"EXEC{order.get('11', '')}"),
        ("150", order.get("150", "2")),
        ("39", order.get("39", "2")),
        ("55", order.get("55", "")),
        ("54", order.get("54", "")),
        ("38", order.get("38", "")),
        ("40", "2"),
        ("44", order.get("44", "")),
        ("58", order.get("58", "Order manually executed"))
    ])

async def process_sta_order(order):
    global exec_seq_num

    print(f"\n[STA] New Order Received:")
    for k, v in order.items():
        print(f" - {k}: {v}")

    print(f"\n🕹️ Please manually place this order in the DMM window.")
    input("✅ When done, press Enter to confirm execution → ")

    order["150"] = "2"
    order["39"] = "2"
    order["58"] = "Order manually executed on DMM"

    exec_report = build_execution_report(order, exec_seq_num)
    exec_seq_num += 1

    for client in execution_clients[:]:
        try:
            client.sendall(exec_report.encode("ascii"))
            print("[RESULT] Sent execution report to STA")
        except Exception as e:
            print(f"[ERROR] Failed to send to STA: {e}")
            execution_clients.remove(client)

class STAOrderHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global seq_num
        client_socket = self.request
        print(f"[5001] STA Connected: {self.client_address}")
        try:
            while True:
                data = b""
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        return
                    data += chunk
                    if b"10=" in data:
                        break

                message = data.decode("ascii", errors="ignore")
                print(f"[5001] Received: {message.replace(SOH, '|')}")
                fix = parse_fix(message)
                msg_type = fix.get("35")

                if msg_type == "A":
                    resp = build_logon_response(seq_num)
                    seq_num += 1
                    client_socket.sendall(resp.encode("ascii"))
                elif msg_type == "D":
                    asyncio.run_coroutine_threadsafe(process_sta_order(fix), asyncio.get_event_loop())
                elif msg_type == "5":
                    return
        except Exception as e:
            print(f"[5001] Error: {e}")

class STAExecutionHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global sta_ready
        print(f"[5002] STA connected for execution results: {self.client_address}")
        execution_clients.append(self.request)
        sta_ready = True
        try:
            while True:
                time.sleep(30)
        except Exception:
            pass
        finally:
            print(f"[5002] STA disconnected")
            if self.request in execution_clients:
                execution_clients.remove(self.request)
            sta_ready = False

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

async def launch_dmm_site():
    global popup_browser
    LOGIN_ID = 'v9411402'
    PASSWORD = 'skwshjdwyd0330'
    URL = "https://demotrade.fx.dmm.com/fxcmdipresen/webrich/direct/login"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(URL)

        await page.fill('input[name="accountId"]', LOGIN_ID)
        await page.fill('input[name="passwordShow"]', PASSWORD)

        async with context.expect_page() as popup_info:
            await page.click('a.c-btn--login')
        popup = await popup_info.value
        await popup.wait_for_load_state()

        try:
            await popup.wait_for_selector('button#commonMessageClose', timeout=15000)
            await popup.click('button#commonMessageClose')
        except PlaywrightTimeout:
            pass

        print("✅ DMM site opened and ready.")
        popup_browser = popup
        set_popup_browser(popup)

        while True:
            await asyncio.sleep(60)  # keep browser open

# Main entry
async def main():
    start_fix_servers()
    await launch_dmm_site()

def start_fix_servers():
    s1 = ThreadedTCPServer((TCP_IP, PORT_STA_ORDERS), STAOrderHandler)
    s2 = ThreadedTCPServer((TCP_IP, PORT_STA_EXECUTIONS), STAExecutionHandler)
    threading.Thread(target=s1.serve_forever, daemon=True).start()
    threading.Thread(target=s2.serve_forever, daemon=True).start()
    print(f"[SERVER] FIX Bridge Started on ports {PORT_STA_ORDERS} / {PORT_STA_EXECUTIONS}")

if __name__ == "__main__":
    asyncio.run(main())

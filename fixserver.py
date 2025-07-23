# fixserver.py
import socketserver
import asyncio
from dmm_api import send_order_to_dmm  # Must be async def send_order_to_dmm(browser, order)
import socketserver
import asyncio
popup_browser = None  # initially None

SOH = '\x01'

def set_popup_browser(popup):
    global popup_browser
    popup_browser = popup
    
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


async def process_order(popup_browser, order, sock, client_addr):
    print(f"[STA] Parsed Order: {order}")
    print(popup_browser,'popup')
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
        global popup_browser
        data = self.request[0].decode('ascii', errors='ignore')
        sock = self.request[1]
        client_addr = self.client_address

        print(f"[STA] Received: {data.replace(SOH, '|')}")
        order = parse_fix(data)

        # Create a new event loop in the current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_order(popup_browser, order, sock, client_addr))
        loop.close()


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 5001
    print(f"[STA] Listening on {HOST}:{PORT}")
    server = ThreadedUDPServer((HOST, PORT), FIXUDPHandler)
    server.serve_forever()

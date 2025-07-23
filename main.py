# main.py
import socket
import threading
import datetime
import time

from fix_builder import build_new_order
from scraper import launch_scraper

UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 5001
UDP_PORT_RECV = 5002

seq_num = 1
last_order_time = 0

def send_fix_udp(message: str, ip=UDP_IP, port=UDP_PORT_SEND):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode('ascii'), (ip, port))
    print("[SENT]", message.replace('\x01', '|'))

def receive_exec_reports():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT_RECV))
    print(f"[LISTEN] Receiving Execution Reports on 0.0.0.0:{UDP_PORT_RECV}")
    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode('ascii')
        print(f"[RECEIVED EXEC REPORT] From {addr}: {msg.replace(chr(1), '|')}")

def send_order_to_sta(symbol: str, side: str, qty: int, price: float):
    global seq_num
    cl_ord_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S%f")[:-3]
    fix_msg = build_new_order(seq_num, cl_ord_id, symbol, side, qty, price)
    send_fix_udp(fix_msg)
    seq_num += 1

def handle_bid_ask(bid, ask):
    global last_order_time
    now = time.time()

    bid_float = float(bid)
    ask_float = float(ask)
    spread = ask_float - bid_float
    # print(f"[SCRAPER] BID: {bid}, ASK: {ask}, Spread: {spread:.5f}")

    if spread < 0.003 and (now - last_order_time) >= 10:
        print("[ORDER] Sending order to STA...")
        send_order_to_sta("USDJPY", "1", 1000000, ask_float)  # 54=1 for Buy
        last_order_time = now

if __name__ == "__main__":
    threading.Thread(target=receive_exec_reports, daemon=True).start()

    # Start the scraper
    from scraper import launch_scraper
    launch_scraper(handle_bid_ask)

import socketserver
import threading
import time
import datetime

SOH = '\x01'

def build_fix_message(fields):
    """
    Build a FIX message string with correct header, body length and checksum.
    Returns bytes encoded in ascii.
    """
    body = SOH.join(f"{tag}={value}" for tag, value in fields) + SOH
    body_length = len(body)
    header = f"8=FIX.4.4{SOH}9={body_length}{SOH}"
    msg = header + body
    checksum = sum(ord(c) for c in msg) % 256
    msg += f"10={checksum:03}{SOH}"
    return msg.encode('ascii')

class FIXHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"[✔] STA connected from {self.client_address}")
        self.running = True
        self.msg_seq_num = 2  # Sequence number for outgoing messages after Logon

        try:
            while self.running:
                data = self.request.recv(4096)
                if not data:
                    break

                decoded = data.decode("ascii")
                print("[📥] Received:")
                print(decoded.replace(SOH, '|'))

                # Respond to Logon (35=A)
                if "35=A" in decoded:
                    print("[🔑] Logon detected, sending Logon Ack")
                    self.send_logon_ack()

                # Detect Logout (35=5)
                if "35=5" in decoded:
                    print("[🔒] Received Logout. Closing session.")
                    self.running = False
                    break

                # Detect New Order Single (35=D)
                if "35=D" in decoded:
                    print("📝 New Order Received!")
                    order = self.parse_fix_message(decoded)
                    clordid = order.get("11", "UNKNOWN")
                    symbol = order.get("55", "???")
                    side = order.get("54", "0")  # 1=Buy, 2=Sell
                    price = order.get("44", "0.0")
                    qty = order.get("38", "0")

                    side_text = "Buy" if side == "1" else ("Sell" if side == "2" else f"Unknown({side})")

                    print(f"→ Order: ClOrdID={clordid}, Symbol={symbol}, Side={side_text}, Qty={qty}, Price={price}")

                    # Send Execution Report ACK
                    exec_report = build_fix_message([
                        ("35", "8"),              # Execution Report
                        ("49", "YOUR_BRIDGE"),    # SenderCompID (server)
                        ("56", "STA"),            # TargetCompID (client)
                        ("34", str(self.msg_seq_num)),
                        ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
                        ("11", clordid),          # ClOrdID
                        ("17", f"EXEC{clordid}"), # ExecID (unique)
                        ("150", "0"),             # ExecType = New
                        ("39", "0"),              # OrdStatus = New
                        ("55", symbol),           # Symbol
                        ("54", side),             # Side
                        ("38", qty),              # OrderQty
                        ("40", "2"),              # OrdType = Limit
                        ("44", price),            # Price
                    ])
                    self.request.sendall(exec_report)
                    print(f"[✅] Sent ExecutionReport (ACK) for order {clordid}")
                    self.msg_seq_num += 1

        except ConnectionResetError:
            print("[✘] STA disconnected unexpectedly")
        finally:
            self.running = False
            try:
                self.request.close()
            except Exception:
                pass
            print("[✘] Connection closed")

    def send_logon_ack(self):
        logon_ack = build_fix_message([
            ("35", "A"),              # MsgType = Logon
            ("49", "YOUR_BRIDGE"),    # SenderCompID (server)
            ("56", "STA"),            # TargetCompID (client)
            ("34", str(self.msg_seq_num)),
            ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
            ("98", "0"),              # Encryption = None
            ("108", "30"),            # HeartBtInt = 30 seconds
            ("141", "Y"),             # ResetSeqNumFlag = Yes
        ])
        self.request.sendall(logon_ack)
        print("[📤] Sent Logon ACK")
        self.msg_seq_num += 1

    def send_quotes_loop(self):
        msg_seq_num = 100  # Start higher to avoid collision with orders
        while self.running:
            time.sleep(2)
            try:
                quote_msg = build_fix_message([
                    ("35", "W"),              # MarketDataSnapshotFullRefresh
                    ("49", "YOUR_BRIDGE"),    # SenderCompID (server)
                    ("56", "STA"),            # TargetCompID (client)
                    ("34", str(msg_seq_num)),
                    ("52", datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")),
                    ("262", "snapshot"),      # MDReqID
                    ("55", "USD/JPY"),        # Symbol
                    ("268", "2"),             # NoMDEntries

                    # MDEntry #1 - Bid
                    ("269", "0"),             # MDEntryType = Bid
                    ("270", "145.334"),       # MDEntryPx
                    ("271", "1.0"),           # MDEntrySize

                    # MDEntry #2 - Ask
                    ("269", "1"),             # MDEntryType = Ask
                    ("270", "145.336"),       # MDEntryPx
                    ("271", "1.0"),           # MDEntrySize
                ])
                self.request.sendall(quote_msg)
                print("[📤] Sent MarketDataSnapshot (W)")
                msg_seq_num += 1
            except OSError:
                print("[⚠️] Socket closed, stopping quote sender.")
                break

    def parse_fix_message(self, message):
        fields = message.strip().split(SOH)
        msg_dict = {}
        for f in fields:
            if '=' in f:
                tag, val = f.split('=', 1)
                msg_dict[tag] = val
        return msg_dict

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 5002
    with ThreadedTCPServer((HOST, PORT), FIXHandler) as server:
        print(f"[🚀] FIX server running on port {PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("[🛑] Server stopped")

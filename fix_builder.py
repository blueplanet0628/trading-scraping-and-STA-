
import datetime

SOH = '\x01'

def calc_checksum(msg: str) -> str:
    chksum = sum(ord(c) for c in msg) % 256
    return f"{chksum:03}"

def build_fix_message(fields):
    body = SOH.join(f"{tag}={val}" for tag, val in fields) + SOH
    header = f"8=FIX.4.4{SOH}9={len(body)}{SOH}"
    msg = header + body
    checksum = calc_checksum(msg)
    return msg + f"10={checksum}{SOH}"

def build_new_order(seq_num: int, cl_ord_id: str, symbol: str, side: str, qty: int, price: float) -> str:
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    side_val = "1" if side.upper() == "BUY" else "2"
    fields = [
        ("35", "D"),               # New Order - Single
        ("34", str(seq_num)),
        ("49", "SOURCE"),          # Replace with your SenderCompID
        ("56", "STA"),             # Replace with your TargetCompID
        ("52", now),
        ("11", cl_ord_id),
        ("55", symbol),
        ("54", side_val),
        ("38", str(qty)),
        ("44", f"{price:.5f}"),
        ("40", "2"),               # Limit Order
    ]
    return build_fix_message(fields)

def build_execution_report(order, seq_num: int, success=True, message: str = "") -> str:
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    fields = [
        ('35', '8'),  # Execution Report
        ('34', str(seq_num)),
        ('49', 'YOUR_BRIDGE'),
        ('56', 'S.T.A.'),
        ('52', now),
        ('11', order.get('11', 'UNKNOWN')),
        ('17', f"EXEC{order.get('11', '')}"),
        ('150', '2' if success else '8'),  # 2 = Filled, 8 = Rejected
        ('39', '2' if success else '8'),   # 2 = Filled, 8 = Rejected
        ('55', order.get('55', '')),
        ('54', order.get('54', '')),
        ('38', order.get('38', '')),
        ('40', '2'),
        ('44', order.get('44', '')),
        ('58', message or ("Order filled successfully" if success else "Order rejected")),
    ]
    return build_fix_message(fields)

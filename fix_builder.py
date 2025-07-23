# fix_builder.py
import datetime

SOH = '\x01'

def calc_checksum(msg: str) -> str:
    chksum = sum(ord(c) for c in msg) % 256
    return f"{chksum:03}"

def build_fix_message(fields):
    body = SOH.join(f"{tag}={val}" for tag, val in fields) + SOH
    header = f"8=FIX.4.2{SOH}9={len(body)}{SOH}"
    msg = header + body
    checksum = calc_checksum(msg)
    return msg + f"10={checksum}{SOH}"

def build_new_order(seq_num: int, cl_ord_id: str, symbol: str, side: str, qty: int, price: float) -> str:
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    side_val = "1" if side.upper() == "BUY" else "2"
    fields = [
        ("35", "D"),               # MsgType New Order Single
        ("34", str(seq_num)),     # MsgSeqNum
        ("49", "SOURCE"),         # SenderCompID
        ("56", "STA"),            # TargetCompID
        ("52", now),              # SendingTime
        ("11", cl_ord_id),        # ClOrdID
        ("55", symbol),           # Symbol
        ("54", side_val),         # Side
        ("38", str(qty)),         # OrderQty
        ("44", f"{price:.5f}"),   # Price
        ("40", "2"),              # OrdType = Limit
    ]
    return build_fix_message(fields)

def build_execution_report(order, success=True, error_message=None):
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    fields = [
        ('35', '8'),  # Execution Report
        ('49', 'STA'),
        ('56', 'SOURCE'),
        ('34', '2'),  # Message sequence number, increment if you want
        ('52', now),
        ('11', order.get('11', 'UNKNOWN')),
        ('17', f"EXEC{order.get('11', '')}"),
        ('150', '0' if success else '8'),  # ExecType: 0=New, 8=Rejected
        ('39', '0' if success else '8'),   # OrdStatus: 0=New, 8=Rejected
        ('55', order.get('55', '')),
        ('54', order.get('54', '')),
        ('38', order.get('38', '')),
        ('44', order.get('44', '')),
    ]
    if not success:
        fields.append(('58', error_message or 'Order Rejected'))

    return build_fix_message(fields)






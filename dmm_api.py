# dmm_ui.py
from playwright.async_api import Page

async def send_order_to_dmm(popup: Page, order: dict) -> tuple[bool, str | None]:
    try:
        symbol = order.get("55")                # e.g. 'USDJPY'
        side = order.get("54")                  # '1' or '2'
        order_lot = order.get("38")             # quantity string
        order_id = order.get("11")              # order id

        print(f"[📡 UI ORDER] {symbol=} {side=} {order_lot=} {order_id=}")

        # 1. Select currency pair
        await popup.wait_for_selector(".currencyPairSelectArea", timeout=5000)
        await popup.select_option('[uifield="currencyPairSelect"]', f'SPOT_{symbol}')

        # 2. Select order type: STREAMING
        await popup.wait_for_selector(".orderTypeSelectArea", timeout=5000)
        await popup.click(".orderTypeSelectArea")
        await popup.click("text=STREAMING")

        # 3. Input order quantity
        await popup.wait_for_selector('[uifield="orderQuantity"]', timeout=5000)
        await popup.fill('[uifield="orderQuantity"]', order_lot)

        # 4. Click Buy/Sell button
        if side == "SELL":
            await popup.wait_for_selector('[uifield="askStreamingButton"]', timeout=5000)
            await popup.click('[uifield="askStreamingButton"]')
        elif side == "BUY":
            await popup.wait_for_selector('[uifield="bidStreamingButton"]', timeout=5000)
            await popup.click('[uifield="bidStreamingButton"]')
        else:
            raise ValueError(f"Invalid side: {side}")

        # 5. Confirm order
        await popup.wait_for_selector('[uifield="orderButtonAll"]', timeout=5000)
        await popup.click('[uifield="orderButtonAll"]')

        # 6. Optional: wait for success message
        await popup.wait_for_selector("#orderSuccess", timeout=10000)
        print(f"[✅ ORDER SUCCESS] Order ID: {order_id}")
        return True, None

    except Exception as e:
        print(f"[❌ ORDER ERROR] {e}")
        return False, str(e)

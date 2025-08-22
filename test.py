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

        # --- Find the draggable window panel containing the div with text '注文タイプ' ---
        panels = popup.locator('div.k-widget.k-window[data-role="draggable"]')
        count = await panels.count()
        target_panel = None
        for i in range(count):
            panel = panels.nth(i)
            title_div = panel.locator('div.orderTypeTitle')
            if await title_div.count() > 0:
                text = await title_div.text_content()
                if text and "注文タイプ" in text:
                    target_panel = panel
                    break
        
        if target_panel is None:
            raise RuntimeError("Could not find the order panel containing '注文タイプ'")

        # --- Click dropdown to open currency pair options ---
                # --- Click dropdown to open currency pair options ---
        dropdown_wrap = target_panel.locator('span.k-dropdown-wrap').first
        await dropdown_wrap.click()
        await asyncio.sleep(0.5)  # Let the dropdown animation complete

        # Locate the hidden <select>
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
            btn = popup.locator('[uifield="bidStreamingButton"]')
        elif side == "2":
            btn = popup.locator('[uifield="askStreamingButton"]')
        else:
            raise ValueError(f"Invalid side value: {side}")

        await btn.wait_for(state="visible", timeout=5000)
        await btn.click()
        print(f"[✅ CLICKED {'BUY' if side == '1' else 'SELL'} BUTTON]")

        order_confirm = popup.locator('button[uifield="orderButtonAll"]')
        await order_confirm.wait_for(state="visible", timeout=7000)
        await order_confirm.click()
        print("[✅ CLICKED ORDER CONFIRM BUTTON]")

        await asyncio.sleep(2)

        execute_button = popup.locator('button[uifield="orderExecuteButton"]')
        await execute_button.wait_for(state="visible", timeout=10000)
        for _ in range(10):
            if await execute_button.is_enabled():
                await execute_button.click()
                print("[✅ CLICKED EXECUTE BUTTON]")
                break
            await asyncio.sleep(0.5)
        else:
            raise TimeoutError("Execute button not enabled in time")


    except Exception as e:
        err_msg = f"{type(e).__name__}: {e}"
        print(f"[❌ ORDER ERROR] {err_msg}")
        return False, {"error": err_msg, "order": order}

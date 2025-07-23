from playwright.async_api import Page
import asyncio

async def send_order_to_dmm(popup: Page, order: dict) -> tuple[bool, str | None]:
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
            # Wait for modal confirmation message to appear
            await popup.wait_for_selector('#layer p.resultMessage:has-text("注文を受け付けました。")', timeout=7000)

            # Locate the unique '閉じる' button
            close_button = popup.locator('#layer button[uifield="closeButton"]', has_text="閉じる")
            await close_button.wait_for(state='visible', timeout=7000)
            await close_button.click()
            print("[✅ 閉じるボタンをクリックしました]")
        except Exception as e:
            print(f"[⚠️ CLOSE WARNING] モーダル閉じる操作失敗: {e}")

        return True, None

    except Exception as e:
        print(f"[❌ ORDER ERROR] {type(e).__name__}: {e}")
        return False, str(e)

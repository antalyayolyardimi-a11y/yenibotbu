import asyncio
import os
from datetime import datetime
from pathlib import Path

from trading_bot.main import Engine
from trading_bot.telegram_bot.bot import BotService


async def main():
    engine = Engine()

    def status_cb():
        return engine.status_text()

    def stats_cb():
        return engine.stats_text()

    # Start Telegram bot if token available
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        bot = BotService(engine.pool, status_cb, stats_cb, engine.tracker)
        
        # Store previous confirmed signals and active trades to detect changes
        prev_confirmed_count = 0
        prev_active_trades = {}

        async def scan_loop():
            nonlocal prev_confirmed_count, prev_active_trades
            
            while True:
                try:
                    await engine.scan_once()
                    
                    # Check for new confirmed signals
                    current_confirmed = engine.get_confirmed_signals()
                    if len(current_confirmed) > prev_confirmed_count:
                        # New confirmed signals - check if they became trades
                        active_trades = engine.get_active_trades()
                        for trade in active_trades:
                            if trade.id not in prev_active_trades:
                                # New trade created from confirmed signal
                                await bot.send_signal_notification(trade)
                    
                    # Check for trade status updates
                    current_active_trades = {t.id: t for t in engine.get_active_trades()}
                    for trade_id, trade in current_active_trades.items():
                        if trade_id in prev_active_trades:
                            prev_trade = prev_active_trades[trade_id]
                            if trade.status != prev_trade.status:
                                # Trade status changed
                                await bot.send_trade_update(trade)
                    
                    # Update tracking variables
                    prev_confirmed_count = len(current_confirmed)
                    prev_active_trades = current_active_trades
                    
                except Exception as e:
                    # surface error through status
                    engine.last_status = f"Hata: {e}"
                await asyncio.sleep(30)

        async def _run():
            # Start scanning in background
            scan_task = asyncio.create_task(scan_loop())
            
            # Run Telegram bot
            try:
                bot.run_polling()
            except KeyboardInterrupt:
                scan_task.cancel()

        await _run()
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN not found. Running in scanning-only mode.")
        print("🔍 For Telegram integration, set TELEGRAM_BOT_TOKEN environment variable.")
        
        # fallback: scanning only
        while True:
            try:
                await engine.scan_once()
                
                # Print signal updates to console
                confirmed = engine.get_confirmed_signals()
                active_trades = engine.get_active_trades()
                
                if confirmed:
                    print(f"✅ Confirmed signals: {len(confirmed)}")
                    
                if active_trades:
                    print(f"💼 Active trades: {len(active_trades)}")
                    for trade in active_trades:
                        print(f"  {trade.symbol} {trade.direction.value} P&L: {trade.current_pnl_pct:.2f}%")
                        
            except Exception as e:
                engine.last_status = f"Hata: {e}"
                print(f"❌ Error: {e}")
            await asyncio.sleep(30)


if __name__ == "__main__":
    print("🚀 15m SMC + Price Action + Order Flow Telegram Bot")
    print("📊 Starting signal generation and validation engine...")
    asyncio.run(main())

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
        bot = BotService(engine.pool, status_cb, stats_cb)

        async def scan_loop():
            while True:
                try:
                    await engine.scan_once()
                except Exception as e:
                    # surface error through status
                    engine.last_status = f"Hata: {e}"
                await asyncio.sleep(30)

        async def _run():
            asyncio.create_task(scan_loop())
            bot.run_polling()

        await _run()
    else:
        # fallback: scanning only
        while True:
            try:
                await engine.scan_once()
            except Exception as e:
                engine.last_status = f"Hata: {e}"
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())

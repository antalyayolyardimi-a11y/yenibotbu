import os
from typing import Optional
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from trading_bot.signals.pool import SignalPool
from trading_bot.ai.nlp import handle_text_command


ALLOWED_IDS_ENV = "TELEGRAM_ALLOWED_USER_IDS"


class BotService:
    def __init__(self, pool: SignalPool, status_cb, stats_cb):
        self.pool = pool
        self.status_cb = status_cb
        self.stats_cb = stats_cb
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN env variable is required")
        self.app = Application.builder().token(token).build()
        self._wire_handlers()
        self.allowed_ids = self._parse_allowed_ids()

    def _wire_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("durum", self.cmd_durum))
        self.app.add_handler(CommandHandler("istatistik", self.cmd_istatistik))
        self.app.add_handler(CommandHandler("havuz", self.cmd_havuz))
        self.app.add_handler(CommandHandler("komut", self.cmd_komut))
        self.app.add_handler(CommandHandler("tp", self.cmd_tp))
        self.app.add_handler(CommandHandler("sl", self.cmd_sl))
        self.app.add_handler(CommandHandler("help", self.cmd_help))

    def _authorized(self, update: Update) -> bool:
        if not self.allowed_ids:
            return True
        uid = update.effective_user.id if update.effective_user else None
        return bool(uid and uid in self.allowed_ids)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        await update.message.reply_text("Merhaba! Komutlar için /help yazın.")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        await update.message.reply_text(
            "/start, /durum, /havuz, /istatistik komutları mevcut."
        )

    async def cmd_durum(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        status = self.status_cb()
        await update.message.reply_text(status)

    async def cmd_istatistik(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        stats = self.stats_cb()
        await update.message.reply_text(stats)

    async def cmd_havuz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        snap = self.pool.snapshot()
        await update.message.reply_text(str(snap))

    async def cmd_komut(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        text = " ".join(context.args) if context.args else ""
        if not text:
            await update.message.reply_text("Kullanım: /komut <metin>")
            return
        resp = handle_text_command(text)
        await update.message.reply_text(resp)

    async def cmd_tp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        await update.message.reply_text("TP durumları: (örnek) henüz işlem takibi yok")

    async def cmd_sl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        await update.message.reply_text("SL durumları: (örnek) henüz işlem takibi yok")

    async def send_message(self, text: str, chat_id: Optional[int] = None):
        await self.app.bot.send_message(chat_id=chat_id or (await self._default_chat_id()), text=text)

    async def _default_chat_id(self) -> Optional[int]:
        updates = await self.app.bot.get_updates()
        for u in reversed(updates):
            if u.message and u.message.chat:
                return u.message.chat.id
        return None

    def run_polling(self):
        self.app.run_polling(allowed_updates=["message", "edited_message"])

    def _parse_allowed_ids(self):
        raw = os.getenv(ALLOWED_IDS_ENV, "").strip()
        ids = []
        if raw:
            for part in raw.split(","):
                part = part.strip()
                if part.isdigit():
                    ids.append(int(part))
        return ids

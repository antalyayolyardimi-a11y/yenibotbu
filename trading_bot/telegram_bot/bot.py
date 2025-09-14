import os
from typing import Optional
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from trading_bot.signals.pool import SignalPool
from trading_bot.ai.nlp import handle_text_command


ALLOWED_IDS_ENV = "TELEGRAM_ALLOWED_USER_IDS"


class BotService:
    def __init__(self, pool: SignalPool, status_cb, stats_cb, tracker=None):
        self.pool = pool
        self.status_cb = status_cb
        self.stats_cb = stats_cb
        self.tracker = tracker
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
        self.app.add_handler(CommandHandler("trades", self.cmd_trades))
        self.app.add_handler(CommandHandler("performance", self.cmd_performance))
        self.app.add_handler(CommandHandler("help", self.cmd_help))

    def _authorized(self, update: Update) -> bool:
        if not self.allowed_ids:
            return True
        uid = update.effective_user.id if update.effective_user else None
        return bool(uid and uid in self.allowed_ids)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        welcome_msg = """🤖 15m SMC + Price Action Sinyal Botu

📊 Mevcut Komutlar:
/durum - Bot durumu ve son tarama
/havuz - Sinyal havuzu (bekleyen/onaylanmış)
/trades - Aktif işlemler
/tp - Take profit durumları
/sl - Stop loss durumları
/istatistik - Performans istatistikleri
/performance - Detaylı analiz
/komut <metin> - Doğal dil komutu
/help - Bu yardım menüsü

🎯 Bot 15m'de sinyal üretir, 5m'de doğrular."""
        await update.message.reply_text(welcome_msg)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        help_msg = """ℹ️ Bot Komutları:

📊 /durum - Son tarama sonuçları
🔍 /havuz - Bekleyen ve onaylanmış sinyaller  
💼 /trades - Aktif işlem takibi
✅ /tp - Take profit durumları
❌ /sl - Stop loss durumları
📈 /istatistik - Temel istatistikler
📊 /performance - Detaylı performans analizi

🗣️ /komut <metin> - Doğal dil komutu örnekleri:
• "RSI periyodunu 14 yap"
• "Stop loss oranını %2'ye çıkar"
• "BTC coinini takipten çıkar"
• "Sadece güçlü sinyalleri işle"

🎯 Bot Çalışma Prensibi:
• 15m grafikte sinyal üretimi
• 5m'de 3 mum doğrulama
• SMC + Price Action + Order Flow
• ATR bazlı SL/TP seviyeleri"""
        await update.message.reply_text(help_msg)

    async def cmd_durum(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        status = self.status_cb()
        await update.message.reply_text(f"📊 Bot Durumu:\n{status}")

    async def cmd_istatistik(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        stats = self.stats_cb()
        await update.message.reply_text(f"📈 İstatistikler:\n{stats}")

    async def cmd_havuz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        snap = self.pool.snapshot()
        
        msg = f"""🔍 Sinyal Havuzu:
        
⏳ Bekleyen: {snap['pending']} sinyal
✅ Onaylanmış: {snap['confirmed']} sinyal

📋 Bekleyen Detay:"""
        
        for sig in snap['pending_details'][:5]:  # Show max 5
            msg += f"\n• {sig['symbol']} {sig['direction'].upper()} ({sig['strength']}) - {sig['age_min']}dk"
            
        if snap['confirmed_details']:
            msg += f"\n\n✅ Onaylanmış Detay:"
            for sig in snap['confirmed_details'][:5]:
                msg += f"\n• {sig['symbol']} {sig['direction'].upper()} ({sig['strength']}) - {sig['age_min']}dk"
        
        await update.message.reply_text(msg)

    async def cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        if not self.tracker:
            await update.message.reply_text("Trade tracker henüz aktif değil.")
            return
            
        active_trades = self.tracker.get_active_trades()
        if not active_trades:
            await update.message.reply_text("💼 Aktif işlem yok.")
            return
            
        msg = f"💼 Aktif İşlemler ({len(active_trades)}):\n"
        for trade in active_trades[:10]:  # Max 10 trades
            status_emoji = "🟢" if trade.direction.value == "long" else "🔴"
            msg += f"\n{status_emoji} {trade.symbol} {trade.direction.value.upper()}"
            msg += f"\n  💰 P&L: {trade.current_pnl_pct:.2f}%"
            msg += f"\n  🎯 Entry: {trade.entry_price:.4f}"
            msg += f"\n  ⛔ SL: {trade.sl_price:.4f}"
            msg += f"\n  ✅ TP1: {trade.tp1_price:.4f}"
            if trade.status.value != "active":
                msg += f"\n  📊 Status: {trade.status.value}"
            msg += "\n"
            
        await update.message.reply_text(msg)

    async def cmd_tp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        if not self.tracker:
            await update.message.reply_text("Trade tracker henüz aktif değil.")
            return
            
        active_trades = self.tracker.get_active_trades()
        tp_trades = [t for t in active_trades if "TP" in t.status.value.upper()]
        
        if not tp_trades:
            await update.message.reply_text("✅ Henüz TP'ye ulaşan işlem yok.")
            return
            
        msg = f"✅ TP Durumları ({len(tp_trades)}):\n"
        for trade in tp_trades:
            msg += f"\n🎯 {trade.symbol} {trade.direction.value.upper()}"
            msg += f"\n  Status: {trade.status.value}"
            msg += f"\n  P&L: {trade.current_pnl_pct:.2f}%"
            if trade.tp1_hit_at:
                msg += f"\n  TP1: ✅"
            if trade.tp2_hit_at:
                msg += f" TP2: ✅"
            if trade.tp3_hit_at:
                msg += f" TP3: 🎯"
            msg += "\n"
            
        await update.message.reply_text(msg)

    async def cmd_sl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        if not self.tracker:
            await update.message.reply_text("Trade tracker henüz aktif değil.")
            return
            
        completed_trades = self.tracker.completed_trades
        sl_trades = [t for t in completed_trades if t.status.value == "sl_hit"]
        
        if not sl_trades:
            await update.message.reply_text("❌ SL'e takılan işlem yok.")
            return
            
        msg = f"❌ SL Durumları (Son {min(len(sl_trades), 10)}):\n"
        for trade in sl_trades[-10:]:  # Last 10
            msg += f"\n🔴 {trade.symbol} {trade.direction.value.upper()}"
            msg += f"\n  P&L: {trade.final_pnl_pct:.2f}%"
            msg += f"\n  MAE: {trade.max_adverse_excursion:.2f}%"
            msg += f"\n  Süre: {(trade.closed_at - trade.created_at).total_seconds()/60:.0f}dk"
            msg += "\n"
            
        await update.message.reply_text(msg)

    async def cmd_performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        if not self.tracker:
            await update.message.reply_text("Trade tracker henüz aktif değil.")
            return
            
        perf = self.tracker.get_performance_analysis()
        if 'error' in perf:
            await update.message.reply_text(f"⚠️ {perf['error']}")
            return
            
        msg = f"""📊 Detaylı Performans Analizi:

📈 Temel İstatistikler:
• Toplam İşlem: {perf['total_trades']}
• Kazanma Oranı: %{perf['win_rate']:.1f}
• Toplam P&L: %{perf['total_pnl']:.2f}
• Ortalama Kazanan: %{perf['avg_winner']:.2f}
• Ortalama Kaybeden: %{perf['avg_loser']:.2f}
• Profit Factor: {perf['profit_factor']:.2f}

📊 Risk Metrikleri:
• Ortalama MAE: %{perf['avg_mae']:.2f}
• Ortalama MFE: %{perf['avg_mfe']:.2f}

🏆 En İyi Semboller:"""

        # Top 3 performing symbols
        symbol_perf = sorted(
            perf['symbol_performance'].items(),
            key=lambda x: x[1]['total_pnl'],
            reverse=True
        )[:3]
        
        for symbol, stats in symbol_perf:
            win_rate = stats['winners'] / stats['trades'] * 100 if stats['trades'] > 0 else 0
            msg += f"\n• {symbol}: %{win_rate:.1f} WR, %{stats['total_pnl']:.2f} P&L"
            
        await update.message.reply_text(msg)

    async def cmd_komut(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            return
        text = " ".join(context.args) if context.args else ""
        if not text:
            await update.message.reply_text("""🗣️ Doğal Dil Komutu Kullanımı:

/komut <metin>

📝 Örnek Komutlar:
• "RSI periyodunu 14 yap"
• "Stop loss oranını %2'ye çıkar"  
• "BTC ve ETH coinlerini takipten çıkar"
• "Sadece güçlü sinyalleri işle"
• "Başarı oranı %30'un altına düşerse stratejiyi değiştir"
• "Volume breakout olan sinyalleri öncelikle"
• "ADX eşiğini 25'e çıkar"

Bot bu komutları anlayıp parametreleri günceller.""")
            return
        resp = handle_text_command(text)
        await update.message.reply_text(f"🤖 Komut yanıtı:\n{resp}")

    async def send_signal_notification(self, trade):
        """Send new confirmed signal notification"""
        message = trade.get_telegram_message()
        await self._send_to_all_chats(message)
        
    async def send_trade_update(self, trade):
        """Send trade status update"""
        message = trade._get_update_message()
        await self._send_to_all_chats(message)

    async def _send_to_all_chats(self, text: str):
        """Send message to all known chats"""
        # For simplicity, we'll use a default chat or the last known chat
        try:
            chat_id = await self._default_chat_id()
            if chat_id:
                await self.app.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            pass  # Silently fail if can't send

    async def send_message(self, text: str, chat_id: Optional[int] = None):
        await self.app.bot.send_message(chat_id=chat_id or (await self._default_chat_id()), text=text)

    async def _default_chat_id(self) -> Optional[int]:
        try:
            updates = await self.app.bot.get_updates()
            for u in reversed(updates):
                if u.message and u.message.chat:
                    return u.message.chat.id
        except:
            pass
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

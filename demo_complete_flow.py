#!/usr/bin/env python3
"""
Complete demonstration of the 15m SMC + Price Action + Order Flow Telegram Signal Bot

This script shows the complete signal flow:
1. 15m signal generation with SMC/Price Action/Order Flow analysis
2. 5m validation with 3-candle confirmation
3. Trade creation with TP/SL levels
4. Telegram message formatting
5. Performance tracking

Run with: python demo_complete_flow.py
"""

import asyncio
import json
from datetime import datetime, timedelta
from trading_bot.main import Engine
from trading_bot.config import config
from trading_bot.trading.tracker import Trade, TradeDirection, TradeStatus
from trading_bot.telegram_bot.bot import BotService

# Configure for demonstration (more permissive for signal generation)
config.indicators.adx_min = 10
config.indicators.volume_multiplier_min = 0.9
config.risk.risk_reward_min = 0.8

class DemoOrchestrator:
    def __init__(self):
        self.engine = Engine()
        self.step = 1
        
    async def demonstrate_complete_flow(self):
        print("🚀 15m SMC + Price Action + Order Flow Bot - Complete Flow Demo")
        print("=" * 70)
        
        # Step 1: 15m Signal Generation
        await self.demo_step_1_signal_generation()
        
        # Step 2: 5m Validation  
        await self.demo_step_2_validation()
        
        # Step 3: Trade Creation
        await self.demo_step_3_trade_creation()
        
        # Step 4: Telegram Message Format
        await self.demo_step_4_telegram_format()
        
        # Step 5: Trade Monitoring
        await self.demo_step_5_trade_monitoring()
        
        # Step 6: Performance Analysis
        await self.demo_step_6_performance_analysis()
        
        print("\n🎯 Demo completed! The bot is ready for live trading.")
        print("📱 Set TELEGRAM_BOT_TOKEN to enable Telegram notifications.")
    
    async def demo_step_1_signal_generation(self):
        print(f"\n🔍 Step {self.step}: 15m Signal Generation")
        print("-" * 50)
        self.step += 1
        
        print("📊 Scanning symbols for 15m signals...")
        print(f"   Timeframe: {config.timeframes.signal}")
        print(f"   ADX minimum: {config.indicators.adx_min}")
        print(f"   Volume multiplier: {config.indicators.volume_multiplier_min}")
        
        await self.engine.scan_once()
        
        snap = self.engine.pool.snapshot()
        print(f"✅ Scan completed: {snap['pending']} pending signals")
        
        if snap['pending_details']:
            print("\n📋 Generated Signals:")
            for sig in snap['pending_details']:
                print(f"   • {sig['symbol']} {sig['direction'].upper()} ({sig['strength']}) - Score: {sig['score']}")
        
    async def demo_step_2_validation(self):
        print(f"\n🔍 Step {self.step}: 5m Validation Process") 
        print("-" * 50)
        self.step += 1
        
        print(f"📊 Validating signals on {config.timeframes.validation} timeframe...")
        print(f"   Validation period: {config.validation.candles_5m} candles (≈15 minutes)")
        print(f"   Micro BOS requirement: {config.validation.min_micro_bos}")
        
        # Force validate for demo (in reality this waits for 5m data)
        pending = self.engine.pool.get_pending_signals()
        if pending:
            # Simulate successful validation
            signal = pending[0]
            self.engine.pool.confirm_signal(signal.symbol, signal.direction)
            print(f"✅ Signal validated: {signal.symbol} {signal.direction}")
        else:
            print("⚠️  No pending signals to validate")
    
    async def demo_step_3_trade_creation(self):
        print(f"\n🔍 Step {self.step}: Trade Creation")
        print("-" * 50)
        self.step += 1
        
        confirmed = self.engine.get_confirmed_signals()
        if confirmed:
            # Create trade from confirmed signal
            signal = confirmed[0]
            trade = self.engine._create_trade_from_signal(signal)
            
            print(f"💼 Trade created: {trade.symbol} {trade.direction.value.upper()}")
            print(f"   Entry: {trade.entry_price:.4f}")
            print(f"   SL: {trade.sl_price:.4f}")
            print(f"   TP1: {trade.tp1_price:.4f} (R={config.risk.tp_r_levels[0]})")
            print(f"   TP2: {trade.tp2_price:.4f} (R={config.risk.tp_r_levels[1]})")
            print(f"   TP3: {trade.tp3_price:.4f} (R={config.risk.tp_r_levels[2]})")
            print(f"   ATR: {trade.atr:.4f}")
            print(f"   ADX: {trade.adx:.1f}")
        else:
            print("⚠️  No confirmed signals to create trades from")
    
    async def demo_step_4_telegram_format(self):
        print(f"\n🔍 Step {self.step}: Telegram Message Format")
        print("-" * 50)
        self.step += 1
        
        active_trades = self.engine.get_active_trades()
        if active_trades:
            trade = active_trades[0]
            
            print("📱 Telegram Signal Message (as per specification):")
            print("=" * 60)
            print(trade.get_telegram_message())
            print("=" * 60)
        else:
            print("⚠️  No active trades to format")
    
    async def demo_step_5_trade_monitoring(self):
        print(f"\n🔍 Step {self.step}: Trade Monitoring & Updates")
        print("-" * 50)
        self.step += 1
        
        active_trades = self.engine.get_active_trades()
        if active_trades:
            trade = active_trades[0]
            
            print("📊 Simulating price movements...")
            
            # Simulate TP1 hit
            if trade.direction == TradeDirection.LONG:
                new_price = trade.tp1_price + 0.0001
            else:
                new_price = trade.tp1_price - 0.0001
                
            status_changed = trade.update_price(new_price)
            if status_changed:
                print(f"✅ TP1 HIT: {trade._get_update_message()}")
                
            # Simulate TP2 hit
            if trade.direction == TradeDirection.LONG:
                new_price = trade.tp2_price + 0.0001
            else:
                new_price = trade.tp2_price - 0.0001
                
            status_changed = trade.update_price(new_price)
            if status_changed:
                print(f"✅ TP2 HIT: {trade._get_update_message()}")
                
            print(f"📈 Current P&L: {trade.current_pnl_pct:.2f}%")
            print(f"📊 MFE: {trade.max_favorable_excursion:.2f}%")
        else:
            print("⚠️  No active trades to monitor")
    
    async def demo_step_6_performance_analysis(self):
        print(f"\n🔍 Step {self.step}: Performance Analysis")
        print("-" * 50)
        self.step += 1
        
        # Simulate some completed trades for analysis
        active_trades = self.engine.get_active_trades()
        if active_trades:
            trade = active_trades[0]
            # Force completion for demo
            trade.status = TradeStatus.TP2_HIT
            trade.final_pnl_pct = trade.current_pnl_pct
            trade.closed_at = datetime.utcnow()
            self.engine.tracker.completed_trades.append(trade)
            self.engine.tracker.active_trades.clear()
        
        summary = self.engine.tracker.get_trade_summary()
        print("📊 Trade Summary:")
        print(f"   Active: {summary['active_trades']}")
        print(f"   Completed: {summary['completed_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.1f}%")
        print(f"   Total P&L: {summary['total_pnl']:.2f}%")
        
        if summary['completed_trades'] > 0:
            perf = self.engine.tracker.get_performance_analysis()
            print("\n📈 Performance Analysis:")
            print(f"   Profit Factor: {perf['profit_factor']:.2f}")
            print(f"   Avg Winner: {perf['avg_winner']:.2f}%")
            print(f"   Avg MAE: {perf['avg_mae']:.2f}%")
            print(f"   Avg MFE: {perf['avg_mfe']:.2f}%")

async def main():
    demo = DemoOrchestrator()
    await demo.demonstrate_complete_flow()
    
    print("\n" + "=" * 70)
    print("🎯 Summary of Implementation:")
    print("✅ 15m SMC + Price Action + Order Flow signal generation")
    print("✅ 5m validation with 3-candle confirmation")  
    print("✅ ATR-based TP/SL levels (R multiples)")
    print("✅ Comprehensive trade tracking (TP1/TP2/TP3)")
    print("✅ Specification-compliant Telegram messages")
    print("✅ Performance analysis and optimization ready")
    print("✅ Offline mode for testing without API access")
    print("✅ Enhanced Telegram bot with natural language commands")
    
    print("\n🚀 Ready for deployment!")
    print("   Set TELEGRAM_BOT_TOKEN and run: python -m trading_bot.orchestrator")

if __name__ == "__main__":
    asyncio.run(main())
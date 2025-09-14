# 🚀 15m SMC + Price Action + Order Flow Telegram Signal Bot

**Professional-grade cryptocurrency trading signal bot implementing 15-minute Smart Money Concepts with automated Telegram notifications.**

## 🎯 Core Features

### 📊 Advanced Signal Generation
- **15-minute primary analysis** with SMC + Price Action + Order Flow
- **5-minute validation** (3-candle confirmation ≈ 15 minutes)
- **Multi-timeframe confluence** detection
- **Institutional methodology** following Smart Money Concepts

### 🔬 Technical Analysis Engine
- **Smart Money Concepts**: BOS/CHOCH, FVG, Order Blocks, Premium/Discount zones
- **Price Action**: Pin bars, engulfing, structure breaks, support/resistance
- **Order Flow**: Volume expansion analysis, flow confirmation  
- **Trend Analysis**: ADX/DI trend strength validation
- **Volatility**: ATR-based dynamic level calculation

### 💼 Professional Trade Management
- **ATR-based SL/TP levels** with R-multiple targets (1R, 1.5R, 2R)
- **Real-time monitoring** with TP1/TP2/TP3 tracking
- **Performance analytics** including MFE/MAE analysis
- **Risk management** with configurable parameters

### 📱 Advanced Telegram Integration
- **Specification-compliant messages** with full technical context
- **Real-time notifications** for all trade status changes
- **Natural language commands** for bot configuration
- **Comprehensive monitoring** tools (/trades, /tp, /sl, /performance)

## 🚀 Quick Start

### Installation
```bash
git clone <repository-url>
cd yenibotbu
pip install -r requirements.txt
cp .env.example .env
```

### Configuration
Edit `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

### Launch
```bash
# With Telegram integration
./start.sh

# Or manually
export TELEGRAM_BOT_TOKEN="your_token"
python -m trading_bot.orchestrator
```

### Demo Mode (No API required)
```bash
# Complete flow demonstration
python demo_complete_flow.py

# Offline testing
python -m trading_bot.main
```

## 📋 Signal Specification

### 15m Signal Generation Requirements
- ✅ **Structure**: BOS or CHOCH confirmation
- ✅ **Trend**: ADX ≥ 20, DI alignment
- ✅ **Volume**: ≥ 1.2x average expansion
- ✅ **Momentum**: RSI alignment (not extremes)
- ✅ **Zone**: OB/FVG/premium-discount interaction
- ✅ **Risk-Reward**: Minimum 1:1 ratio

### 5m Validation (3 candles)
- ✅ **Price maintenance**: Entry zone preserved
- ✅ **Micro structure**: ≥1 micro BOS required
- ✅ **Volume consistency**: No significant drops

### Telegram Message Format
```
[15m SİNYAL] BTC/USDT LONG 🟢
Giriş: 60000.0000 | SL: 58440.0000
TP1: 61560.0000 | TP2: 62040.0000 | TP3: 62520.0000
ATR(14): 1040.0000 | ADX(14): 25.5 | DI+: 28.3 / DI-: 15.7
Yapı: BOS=1/CHOCH=0 | Bölge: Bullish OB
Hacim sapması: 1.8x | Momentum: uyumlu
Zaman damgası: 2025-01-15T10:30:00 | Borsa: kucoin
```

## 🤖 Telegram Commands

### Basic Commands
```
/start          - Bot overview and welcome
/help           - Complete command reference  
/durum          - Current status and last scan
/havuz          - Signal pool status
/istatistik     - Performance statistics
```

### Trade Monitoring
```
/trades         - Active positions
/tp             - Take profit updates
/sl             - Stop loss alerts
/performance    - Detailed analytics
```

### Natural Language Configuration
```
/komut "RSI periyodunu 14 yap"
/komut "Stop loss oranını %2'ye çıkar"
/komut "BTC coinini takipten çıkar"
/komut "Sadece güçlü sinyalleri işle"
```

## ⚙️ Configuration

### Key Parameters
```python
# Timeframes
signal = "15m"              # Primary analysis
validation = "5m"           # Confirmation period

# Signal Requirements  
adx_min = 20               # Minimum trend strength
volume_multiplier_min = 1.2 # Volume expansion threshold
risk_reward_min = 1.0      # Minimum R:R ratio

# Risk Management
sl_atr_mult = 1.5          # SL = entry ± (1.5 × ATR)
tp_r_levels = [1.0, 1.5, 2.0]  # TP targets
```

## 🏗️ Architecture

### Signal Flow
```
15m Analysis → SMC + Price Action + Order Flow → Signal Pool
     ↓
5m Validation → 3 Candle Confirmation → Trade Creation
     ↓  
Trade Tracker → TP/SL Monitoring → Telegram Updates
     ↓
Performance Analysis → Parameter Optimization
```

### Core Modules
- **Signal Engine**: 15m generation with full technical analysis
- **Validation Engine**: 5m confirmation with micro structure
- **Trade Tracker**: Real-time TP/SL monitoring with MFE/MAE
- **Telegram Bot**: Professional messaging with natural language
- **Performance Analyzer**: Win rate, profit factor, optimization

## 📊 Performance Features

### Analytics
- **Real-time P&L tracking** with floating/realized breakdown
- **Win rate analysis** by symbol and timeframe
- **R-multiple distribution** and profit factor calculation
- **MFE/MAE metrics** for trade quality assessment
- **Drawdown analysis** and risk metrics

### Optimization
- **Adaptive parameters** based on performance feedback
- **Market regime detection** (trend vs range conditions)
- **Success rate monitoring** with automatic adjustments
- **Audit trail** for all configuration changes

## 🔐 Security & Safety

### Design Principles
- ✅ **API keyless operation** (market data only)
- ✅ **No trade execution** (signals only)
- ✅ **User authorization** via Telegram IDs
- ✅ **Local data storage** (JSON files)
- ✅ **Graceful error handling**

### Data Privacy
- ✅ **No external data sharing**
- ✅ **Secure environment variables**
- ✅ **Rate limiting compliance**
- ✅ **Audit logging**

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Complete setup instructions
- **[Demo Script](demo_complete_flow.py)**: Full flow demonstration
- **[Configuration](trading_bot/config.py)**: All parameters
- **[Examples](#)**: Signal messages and command usage

## 🎯 Use Cases

### For Traders
- **Signal generation** with institutional methodology
- **Risk management** with precise TP/SL levels
- **Performance tracking** with detailed analytics
- **Mobile alerts** via Telegram

### For Developers
- **Modular architecture** for easy extension
- **Clean separation** of concerns
- **Comprehensive testing** with offline mode
- **Well-documented** codebase

### For Analysts
- **Market structure** analysis with SMC
- **Volume flow** confirmation
- **Multi-timeframe** confluence
- **Historical performance** data

## ⚠️ Important Notes

### What This Bot Does
- ✅ **Generates trading signals** using advanced TA
- ✅ **Provides risk levels** (SL/TP1/TP2/TP3)
- ✅ **Tracks performance** with detailed metrics
- ✅ **Sends notifications** via Telegram

### What This Bot Does NOT Do
- ❌ **Execute trades** automatically
- ❌ **Guarantee profits** or success
- ❌ **Provide financial advice**
- ❌ **Access your trading accounts**

### Risk Disclaimer
This software is for educational and informational purposes only. Cryptocurrency trading involves substantial risk of loss. Users are responsible for their own trading decisions and risk management. Always perform your own analysis and never risk more than you can afford to lose.

---

## 🔄 Updates & Support

**Latest Version**: Implements complete 15m SMC + Price Action + Order Flow specification
**Status**: ✅ Ready for deployment
**Documentation**: Complete with examples and troubleshooting
**Testing**: Offline mode available for safe testing

For support, issues, or feature requests, please use the GitHub repository tools.
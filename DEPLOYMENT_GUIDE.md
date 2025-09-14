# 🚀 15m SMC + Price Action + Order Flow Telegram Signal Bot

## Overview

This is a professional-grade cryptocurrency trading signal bot that implements **15-minute Smart Money Concepts (SMC) + Price Action + Order Flow** analysis with automatic Telegram notifications. The bot follows institutional trading methodology and provides precise entry/exit signals with comprehensive risk management.

## Key Features

### 🎯 Signal Generation Engine
- **15-minute timeframe** primary analysis
- **5-minute validation** with 3-candle confirmation (≈15 minutes)
- **Smart Money Concepts**: Market structure (HH/HL/LH/LL), BOS/CHOCH, FVG, Order Blocks, Premium/Discount zones
- **Price Action**: Pin bars, engulfing patterns, structure breaks, support/resistance
- **Order Flow**: Volume expansion analysis, flow confirmation
- **Technical indicators**: ADX/DI (trend strength), ATR (volatility), RSI (momentum alignment)

### 💼 Advanced Trade Management
- **ATR-based levels**: Dynamic SL/TP calculation
- **R-multiple targets**: TP1 (1R), TP2 (1.5R), TP3 (2R)
- **Real-time monitoring**: Automatic TP/SL tracking
- **Performance metrics**: MFE/MAE analysis, win rate, profit factor

### 📱 Professional Telegram Integration
- **Specification-compliant messages** with all technical details
- **Real-time updates** for TP/SL hits
- **Natural language commands** for bot configuration
- **Comprehensive monitoring**: /trades, /tp, /sl, /performance commands

## Installation

### Prerequisites
```bash
python >= 3.12
pip install -r requirements.txt
```

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd yenibotbu

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Environment Configuration
Edit `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

## Usage

### Start the Bot
```bash
# With Telegram integration
./start.sh

# Or manually
export TELEGRAM_BOT_TOKEN="your_token"
python -m trading_bot.orchestrator
```

### Demo Mode (No API required)
```bash
# Test with simulated data
python demo_complete_flow.py

# Scanning only
python -m trading_bot.main
```

## Signal Flow

### 1. 15m Signal Generation
The bot scans configured symbols every 30 seconds on the 15-minute timeframe:

**Required Conditions:**
- ✅ **Structure confirmation**: BOS or CHOCH detected
- ✅ **Trend strength**: ADX ≥ 20 (configurable)
- ✅ **Direction alignment**: DI+/DI- supporting signal direction
- ✅ **Volume confirmation**: Volume ≥ 1.2x average (configurable)
- ✅ **Momentum alignment**: RSI not in extreme zones
- ✅ **Zone interaction**: Price near OB/FVG/premium-discount zones
- ✅ **Risk-reward**: Minimum 1:1 R:R ratio (configurable)

### 2. 5m Validation (15-minute window)
Signals are validated on 5-minute timeframe for 3 candles:

**Validation Criteria:**
- ✅ **Price maintenance**: Entry zone preserved (±2% tolerance)
- ✅ **Micro structure**: At least 1 micro BOS in signal direction
- ✅ **Volume consistency**: No significant volume drop (unless allowed)

### 3. Trade Creation & Monitoring
Validated signals become active trades with:

**Automatic Levels:**
- **Entry**: Signal candle close or limit zone
- **SL**: Entry ± (1.5 × ATR) - configurable
- **TP1**: Entry + (1.0 × Risk) - 1R target
- **TP2**: Entry + (1.5 × Risk) - 1.5R target  
- **TP3**: Entry + (2.0 × Risk) - 2R target

## Telegram Commands

### Basic Commands
```
/start          - Welcome message and overview
/help           - Detailed command reference
/durum          - Current bot status and last scan
/havuz          - Signal pool (pending/confirmed)
/istatistik     - Basic performance statistics
```

### Trade Monitoring
```
/trades         - Active trade positions
/tp             - Take profit status updates
/sl             - Stop loss occurrences
/performance    - Detailed performance analysis
```

### Advanced Commands
```
/komut <text>   - Natural language configuration

Examples:
• "RSI periyodunu 14 yap"
• "Stop loss oranını %2'ye çıkar"  
• "BTC coinini takipten çıkar"
• "Sadece güçlü sinyalleri işle"
• "ADX eşiğini 25'e çıkar"
```

## Configuration

### Key Parameters (`trading_bot/config.py`)
```python
# Timeframes
signal = "15m"           # Primary analysis
validation = "5m"        # Confirmation timeframe

# Indicators  
adx_min = 20            # Minimum trend strength
volume_multiplier_min = 1.2  # Volume expansion threshold
atr_period = 14         # ATR calculation period

# Risk Management
sl_atr_mult = 1.5       # SL = entry ± (1.5 × ATR)
tp_r_levels = [1.0, 1.5, 2.0]  # TP targets in R multiples
risk_reward_min = 1.0   # Minimum R:R ratio

# Validation
candles_5m = 3          # 5m validation period
min_micro_bos = 1       # Required micro BOS count
```

## Message Examples

### New Signal Notification
```
[15m SİNYAL] BTC/USDT LONG 🟢
Giriş: 60000.0000 | SL: 58440.0000
TP1: 61560.0000 | TP2: 62040.0000 | TP3: 62520.0000
ATR(14): 1040.0000 | ADX(14): 25.5 | DI+: 28.3 / DI-: 15.7
Yapı: BOS=1/CHOCH=0 | Bölge: Bullish OB
Hacim sapması: 1.8x | Momentum: uyumlu
Zaman damgası: 2025-01-15T10:30:00 | Borsa: kucoin
```

### Trade Updates
```
✅ BTC/USDT LONG - TP1 geldi! (+2.67%)
✅ BTC/USDT LONG - TP2 geldi! (+3.50%)
🎯 BTC/USDT LONG - TP3 geldi! (+4.33%)
❌ ETH/USDT SHORT - SL oldu (-1.5%)
```

## Performance Features

### Automatic Analysis
- **Win rate tracking** with symbol breakdown
- **R-multiple distribution** analysis
- **MFE/MAE metrics** for optimization
- **Time-based performance** tracking
- **Profit factor** calculation

### Optimization Ready
- **Parameter adaptation** based on performance
- **Market regime detection** (trend/range)
- **Success rate monitoring** with alerts
- **Configuration versioning** for audit trail

## Architecture

### Core Modules
```
trading_bot/
├── main.py              # Signal generation engine
├── orchestrator.py      # Main coordinator with Telegram
├── config.py           # Configuration management
├── indicators/ta.py    # Technical indicators
├── technical/smc.py    # Smart Money Concepts
├── technical/price_action.py  # Price action patterns
├── signals/pool.py     # Signal validation pool
├── trading/tracker.py  # Trade tracking system
├── telegram_bot/bot.py # Telegram integration
└── exchange/kucoin_client.py  # Market data
```

### Data Flow
```
15m OHLCV → SMC Analysis → Price Action → Signal Generation
     ↓
5m Validation Pool → 3 Candle Confirmation → Trade Creation
     ↓
Trade Tracker → TP/SL Monitoring → Telegram Updates
     ↓
Performance Analysis → Parameter Optimization
```

## Security & Compliance

### Safety Features
- ✅ **API keyless operation** (market data only)
- ✅ **No order execution** (signals only)
- ✅ **User authorization** via Telegram IDs
- ✅ **Rate limiting** compliance
- ✅ **Error handling** with graceful degradation

### Data Privacy
- ✅ **Local storage** only (JSON files)
- ✅ **No external data sharing**
- ✅ **Secure token handling**
- ✅ **Audit trail** for all changes

## Troubleshooting

### Common Issues

**Bot not starting:**
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Test connection
python -c "from telegram import Bot; Bot('your_token').get_me()"
```

**No signals generated:**
```bash
# Check parameters
python -c "from trading_bot.config import config; print(config.indicators.adx_min)"

# Run demo with relaxed conditions
python demo_complete_flow.py
```

**Telegram not responding:**
```bash
# Check user permissions
export TELEGRAM_ALLOWED_USER_IDS="your_user_id"

# Test authorization
/start command in Telegram
```

## Development

### Running Tests
```bash
# Import tests
python -c "from trading_bot.main import Engine; print('✅ Imports OK')"

# Signal generation test
python demo_complete_flow.py

# Offline mode test
python -m trading_bot.main
```

### Adding Features
1. **New indicators**: Add to `indicators/ta.py`
2. **SMC patterns**: Extend `technical/smc.py`
3. **Telegram commands**: Update `telegram_bot/bot.py`
4. **Configuration**: Modify `config.py`

## Support

### Documentation
- **Specification**: See original problem statement
- **Code documentation**: Inline comments
- **Examples**: `demo_complete_flow.py`

### Community
- **Issues**: GitHub issue tracker
- **Discussions**: Repository discussions
- **Updates**: Watch repository for releases

---

## ⚠️ Disclaimer

This software is for educational and informational purposes only. It provides trading signals but does not execute trades. Users are responsible for their own trading decisions and risk management. Cryptocurrency trading involves substantial risk of loss.

**The bot:**
- ✅ Generates signals based on technical analysis
- ✅ Provides risk management levels
- ❌ Does NOT execute trades automatically
- ❌ Does NOT guarantee profits
- ❌ Is NOT financial advice

Always perform your own analysis and never risk more than you can afford to lose.
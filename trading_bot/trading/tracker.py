from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum
import json


class TradeStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit"
    TP3_HIT = "tp3_hit"
    SL_HIT = "sl_hit"
    CLOSED = "closed"


class TradeDirection(Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class Trade:
    id: str
    symbol: str
    direction: TradeDirection
    entry_price: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    tp3_price: float
    
    # Technical context
    atr: float
    adx: float
    di_plus: float
    di_minus: float
    structure_info: str
    zone_info: str
    volume_multiplier: float
    momentum_status: str
    
    # Timestamps
    created_at: datetime
    activated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Status tracking
    status: TradeStatus = TradeStatus.PENDING
    tp1_hit_at: Optional[datetime] = None
    tp2_hit_at: Optional[datetime] = None
    tp3_hit_at: Optional[datetime] = None
    
    # Performance tracking
    max_favorable_excursion: float = 0.0  # MFE
    max_adverse_excursion: float = 0.0    # MAE
    current_pnl_pct: float = 0.0
    final_pnl_pct: Optional[float] = None
    
    # Meta
    meta: Dict = field(default_factory=dict)
    
    def update_price(self, current_price: float) -> bool:
        """Update trade with current price, return True if status changed"""
        if self.status in [TradeStatus.CLOSED, TradeStatus.SL_HIT]:
            return False
            
        old_status = self.status
        
        # Calculate current P&L
        if self.direction == TradeDirection.LONG:
            pnl_pct = (current_price - self.entry_price) / self.entry_price * 100
        else:
            pnl_pct = (self.entry_price - current_price) / self.entry_price * 100
            
        self.current_pnl_pct = pnl_pct
        
        # Update MFE and MAE
        if pnl_pct > 0:
            self.max_favorable_excursion = max(self.max_favorable_excursion, pnl_pct)
        else:
            self.max_adverse_excursion = max(self.max_adverse_excursion, abs(pnl_pct))
        
        # Check TP/SL levels
        if self.direction == TradeDirection.LONG:
            if current_price <= self.sl_price:
                self.status = TradeStatus.SL_HIT
                self.final_pnl_pct = pnl_pct
                self.closed_at = datetime.utcnow()
            elif current_price >= self.tp3_price and self.status != TradeStatus.TP3_HIT:
                self.status = TradeStatus.TP3_HIT
                self.tp3_hit_at = datetime.utcnow()
            elif current_price >= self.tp2_price and self.status not in [TradeStatus.TP2_HIT, TradeStatus.TP3_HIT]:
                self.status = TradeStatus.TP2_HIT
                self.tp2_hit_at = datetime.utcnow()
            elif current_price >= self.tp1_price and self.status not in [TradeStatus.TP1_HIT, TradeStatus.TP2_HIT, TradeStatus.TP3_HIT]:
                self.status = TradeStatus.TP1_HIT
                self.tp1_hit_at = datetime.utcnow()
        else:  # SHORT
            if current_price >= self.sl_price:
                self.status = TradeStatus.SL_HIT
                self.final_pnl_pct = pnl_pct
                self.closed_at = datetime.utcnow()
            elif current_price <= self.tp3_price and self.status != TradeStatus.TP3_HIT:
                self.status = TradeStatus.TP3_HIT
                self.tp3_hit_at = datetime.utcnow()
            elif current_price <= self.tp2_price and self.status not in [TradeStatus.TP2_HIT, TradeStatus.TP3_HIT]:
                self.status = TradeStatus.TP2_HIT
                self.tp2_hit_at = datetime.utcnow()
            elif current_price <= self.tp1_price and self.status not in [TradeStatus.TP1_HIT, TradeStatus.TP2_HIT, TradeStatus.TP3_HIT]:
                self.status = TradeStatus.TP1_HIT
                self.tp1_hit_at = datetime.utcnow()
        
        return old_status != self.status
    
    def get_telegram_message(self) -> str:
        """Generate Telegram message format as per specification"""
        direction_emoji = "🟢" if self.direction == TradeDirection.LONG else "🔴"
        
        if self.status == TradeStatus.PENDING:
            return f"""[15m SİNYAL] {self.symbol} {self.direction.value.upper()} {direction_emoji}
Giriş: {self.entry_price:.4f} | SL: {self.sl_price:.4f}
TP1: {self.tp1_price:.4f} | TP2: {self.tp2_price:.4f} | TP3: {self.tp3_price:.4f}
ATR(14): {self.atr:.4f} | ADX(14): {self.adx:.1f} | DI+: {self.di_plus:.1f} / DI-: {self.di_minus:.1f}
Yapı: {self.structure_info} | Bölge: {self.zone_info}
Hacim sapması: {self.volume_multiplier:.1f}x | Momentum: {self.momentum_status}
Zaman damgası: {self.created_at.isoformat()} | Borsa: kucoin"""
        else:
            return self._get_update_message()
    
    def _get_update_message(self) -> str:
        """Generate update message for TP/SL hits"""
        if self.status == TradeStatus.TP1_HIT:
            return f"✅ {self.symbol} {self.direction.value.upper()} - TP1 geldi! ({self.current_pnl_pct:.2f}%)"
        elif self.status == TradeStatus.TP2_HIT:
            return f"✅ {self.symbol} {self.direction.value.upper()} - TP2 geldi! ({self.current_pnl_pct:.2f}%)"
        elif self.status == TradeStatus.TP3_HIT:
            return f"🎯 {self.symbol} {self.direction.value.upper()} - TP3 geldi! ({self.current_pnl_pct:.2f}%)"
        elif self.status == TradeStatus.SL_HIT:
            return f"❌ {self.symbol} {self.direction.value.upper()} - SL oldu ({self.current_pnl_pct:.2f}%)"
        else:
            return f"📊 {self.symbol} {self.direction.value.upper()} - Devam ediyor ({self.current_pnl_pct:.2f}%)"


class TradeTracker:
    def __init__(self):
        self.active_trades: Dict[str, Trade] = {}
        self.completed_trades: List[Trade] = []
        
    def add_trade(self, trade: Trade) -> str:
        """Add a new trade to tracking"""
        self.active_trades[trade.id] = trade
        trade.status = TradeStatus.ACTIVE
        trade.activated_at = datetime.utcnow()
        return trade.id
        
    def update_prices(self, prices: Dict[str, float]) -> List[Trade]:
        """Update all active trades with current prices, return trades with status changes"""
        updated_trades = []
        trades_to_close = []
        
        for trade_id, trade in self.active_trades.items():
            if trade.symbol in prices:
                current_price = prices[trade.symbol]
                if trade.update_price(current_price):
                    updated_trades.append(trade)
                    
                    # Move completed trades
                    if trade.status in [TradeStatus.SL_HIT, TradeStatus.TP3_HIT]:
                        trades_to_close.append(trade_id)
        
        # Move completed trades
        for trade_id in trades_to_close:
            trade = self.active_trades.pop(trade_id)
            self.completed_trades.append(trade)
            
        return updated_trades
    
    def get_active_trades(self) -> List[Trade]:
        """Get all active trades"""
        return list(self.active_trades.values())
    
    def get_trade_summary(self) -> Dict:
        """Get summary of all trades"""
        active = len(self.active_trades)
        completed = len(self.completed_trades)
        
        if completed > 0:
            winners = sum(1 for t in self.completed_trades if t.final_pnl_pct and t.final_pnl_pct > 0)
            total_pnl = sum(t.final_pnl_pct or 0 for t in self.completed_trades)
            win_rate = winners / completed * 100
        else:
            winners = 0
            total_pnl = 0
            win_rate = 0
            
        return {
            'active_trades': active,
            'completed_trades': completed,
            'winners': winners,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / completed if completed > 0 else 0
        }
    
    def get_performance_analysis(self) -> Dict:
        """Detailed performance analysis for optimization"""
        if not self.completed_trades:
            return {'error': 'No completed trades for analysis'}
            
        # Basic stats
        winner_trades = [t for t in self.completed_trades if t.final_pnl_pct and t.final_pnl_pct > 0]
        loser_trades = [t for t in self.completed_trades if t.final_pnl_pct and t.final_pnl_pct <= 0]
        
        total_trades = len(self.completed_trades)
        win_rate = len(winner_trades) / total_trades * 100
        
        # P&L analysis
        total_pnl = sum(t.final_pnl_pct or 0 for t in self.completed_trades)
        avg_winner = sum(t.final_pnl_pct for t in winner_trades) / len(winner_trades) if winner_trades else 0
        avg_loser = sum(t.final_pnl_pct for t in loser_trades) / len(loser_trades) if loser_trades else 0
        
        # Risk metrics
        avg_mae = sum(t.max_adverse_excursion for t in self.completed_trades) / total_trades
        avg_mfe = sum(t.max_favorable_excursion for t in self.completed_trades) / total_trades
        
        # Symbol performance
        symbol_stats = {}
        for trade in self.completed_trades:
            symbol = trade.symbol
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'trades': 0, 'winners': 0, 'total_pnl': 0}
            symbol_stats[symbol]['trades'] += 1
            if trade.final_pnl_pct and trade.final_pnl_pct > 0:
                symbol_stats[symbol]['winners'] += 1
            symbol_stats[symbol]['total_pnl'] += trade.final_pnl_pct or 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_winner': avg_winner,
            'avg_loser': avg_loser,
            'profit_factor': abs(avg_winner * len(winner_trades) / (avg_loser * len(loser_trades))) if loser_trades else float('inf'),
            'avg_mae': avg_mae,
            'avg_mfe': avg_mfe,
            'symbol_performance': symbol_stats
        }
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        return {
            'active_trades': {k: self._trade_to_dict(v) for k, v in self.active_trades.items()},
            'completed_trades': [self._trade_to_dict(t) for t in self.completed_trades]
        }
    
    def from_dict(self, data: Dict):
        """Deserialize from dictionary"""
        self.active_trades = {k: self._dict_to_trade(v) for k, v in data.get('active_trades', {}).items()}
        self.completed_trades = [self._dict_to_trade(t) for t in data.get('completed_trades', [])]
    
    def _trade_to_dict(self, trade: Trade) -> Dict:
        """Convert Trade to dictionary"""
        return {
            'id': trade.id,
            'symbol': trade.symbol,
            'direction': trade.direction.value,
            'entry_price': trade.entry_price,
            'sl_price': trade.sl_price,
            'tp1_price': trade.tp1_price,
            'tp2_price': trade.tp2_price,
            'tp3_price': trade.tp3_price,
            'atr': trade.atr,
            'adx': trade.adx,
            'di_plus': trade.di_plus,
            'di_minus': trade.di_minus,
            'structure_info': trade.structure_info,
            'zone_info': trade.zone_info,
            'volume_multiplier': trade.volume_multiplier,
            'momentum_status': trade.momentum_status,
            'created_at': trade.created_at.isoformat(),
            'activated_at': trade.activated_at.isoformat() if trade.activated_at else None,
            'closed_at': trade.closed_at.isoformat() if trade.closed_at else None,
            'status': trade.status.value,
            'tp1_hit_at': trade.tp1_hit_at.isoformat() if trade.tp1_hit_at else None,
            'tp2_hit_at': trade.tp2_hit_at.isoformat() if trade.tp2_hit_at else None,
            'tp3_hit_at': trade.tp3_hit_at.isoformat() if trade.tp3_hit_at else None,
            'max_favorable_excursion': trade.max_favorable_excursion,
            'max_adverse_excursion': trade.max_adverse_excursion,
            'current_pnl_pct': trade.current_pnl_pct,
            'final_pnl_pct': trade.final_pnl_pct,
            'meta': trade.meta
        }
    
    def _dict_to_trade(self, data: Dict) -> Trade:
        """Convert dictionary to Trade"""
        return Trade(
            id=data['id'],
            symbol=data['symbol'],
            direction=TradeDirection(data['direction']),
            entry_price=data['entry_price'],
            sl_price=data['sl_price'],
            tp1_price=data['tp1_price'],
            tp2_price=data['tp2_price'],
            tp3_price=data['tp3_price'],
            atr=data['atr'],
            adx=data['adx'],
            di_plus=data['di_plus'],
            di_minus=data['di_minus'],
            structure_info=data['structure_info'],
            zone_info=data['zone_info'],
            volume_multiplier=data['volume_multiplier'],
            momentum_status=data['momentum_status'],
            created_at=datetime.fromisoformat(data['created_at']),
            activated_at=datetime.fromisoformat(data['activated_at']) if data['activated_at'] else None,
            closed_at=datetime.fromisoformat(data['closed_at']) if data['closed_at'] else None,
            status=TradeStatus(data['status']),
            tp1_hit_at=datetime.fromisoformat(data['tp1_hit_at']) if data['tp1_hit_at'] else None,
            tp2_hit_at=datetime.fromisoformat(data['tp2_hit_at']) if data['tp2_hit_at'] else None,
            tp3_hit_at=datetime.fromisoformat(data['tp3_hit_at']) if data['tp3_hit_at'] else None,
            max_favorable_excursion=data['max_favorable_excursion'],
            max_adverse_excursion=data['max_adverse_excursion'],
            current_pnl_pct=data['current_pnl_pct'],
            final_pnl_pct=data['final_pnl_pct'],
            meta=data['meta']
        )
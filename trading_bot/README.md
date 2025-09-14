Akıllı Kripto Trading Botu (iskelet)

Uyarı: Bu repo, sinyal üretimi ve Telegram ile raporlamayı hedefleyen bir iskelet uygulamadır.
Gerçek para ile işlem yapmaz; yalnızca veri çeker ve sinyal havuzuna ekler.

Hızlı Başlangıç

1) Bağımlılıkları kurun:

```bash
pip install -r requirements.txt
```

2) Çevre değişkenini ayarlayın (Telegram için opsiyonel):

```bash
export TELEGRAM_BOT_TOKEN="123:ABC..."
export TELEGRAM_ALLOWED_USER_IDS="123456789,987654321"
```

3) Çalıştırın (sadece tarama döngüsü):

```bash
python -m trading_bot.main
```

4) Telegram ile orchestrator:

```bash
python -m trading_bot.orchestrator
```

Alternatif: .env ile ve tek komutla başlatma

```bash
cp .env.example .env
# .env içini düzenleyin (TOKEN vs.)
./start.sh
```

Notlar

- KuCoin verileri için API anahtarı gerekmez; ccxt fetch_ohlcv kullanır.
- ATR tabanlı SL/TP seviyeleri ve skorlamaya göre havuza sinyal düşer.
- Telegram bütünleşmesi için trading_bot/telegram_bot/bot.py dosyasına bakın.

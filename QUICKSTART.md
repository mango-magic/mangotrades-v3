# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
python3 -c "from database import init_db; init_db()"
```

### Step 3: Start the Server

```bash
python3 app.py
```

Then open your browser to: **http://localhost:5000**

## 📋 What You Can Do

### 1. Check Stock Prices
- Click "Check All Stocks" button in the dashboard
- Or use API: `POST http://localhost:5000/api/stocks/check`
- This will check all 7,000+ stocks from your CSV file

### 2. Generate AI Signals
- Click "Generate Signals" button in the dashboard
- Or use API: `POST http://localhost:5000/api/ai/signals/generate`
- AI will analyze stocks and generate buy/sell/hold signals

### 3. Place Trades
- Use the "Place Trade" form in the dashboard
- Enter ticker, quantity, side (buy/sell), and order type
- Orders will be placed through Alpaca paper trading

### 4. View Portfolio
- Dashboard automatically shows:
  - Portfolio value
  - Buying power
  - Open positions
  - Unrealized P&L
  - Recent trades

## ⏰ Automated Scheduling

To run automatic stock checks at 10 AM EST daily:

```bash
python3 run_scheduler.py
```

This will:
- Check all stocks at 10:00 AM EST
- Generate AI signals at 10:30 AM EST

## 🔧 Manual Operations

### Check a Single Stock Price
```python
from stock_checker import StockChecker
checker = StockChecker()
price = checker.get_stock_price("AAPL")
print(price)
```

### Generate Signal for One Stock
```python
from ai_decision import AIDecisionMaker
ai = AIDecisionMaker()
signal = ai.generate_signal("AAPL")
print(signal)
```

### Place a Trade Programmatically
```python
from alpaca_client import AlpacaClient
client = AlpacaClient()
order = client.place_market_order("AAPL", 10, "buy")
print(order)
```

## 📊 API Examples

### Get Account Info
```bash
curl http://localhost:5000/api/account
```

### Get Positions
```bash
curl http://localhost:5000/api/positions
```

### Get Latest Prices
```bash
curl http://localhost:5000/api/stocks/prices?limit=50
```

### Get AI Signals
```bash
curl http://localhost:5000/api/ai/signals?limit=20
```

### Place a Trade
```bash
curl -X POST http://localhost:5000/api/trades \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "quantity": 10,
    "side": "buy",
    "order_type": "market"
  }'
```

## 🐛 Troubleshooting

### "Module not found" errors
- Make sure you've installed all dependencies: `pip install -r requirements.txt`

### "Database locked" errors
- Close any other processes using the database
- Delete `mangotrades.db` and reinitialize

### API connection errors
- Verify your Alpaca API keys in `.env` file
- Check your internet connection
- Ensure Alpaca paper trading account is active

### Stock check taking too long
- This is normal! Checking 7,000+ stocks takes time
- The system includes rate limiting to avoid API issues
- Progress is shown in the console

## 💡 Tips

1. **Start Small**: Test with a few stocks before checking all 7,000+
2. **Paper Trading**: All trades go through Alpaca's paper trading (no real money)
3. **Monitor Logs**: Check console output for errors and progress
4. **Database**: All data is stored in `mangotrades.db` SQLite database
5. **Schedule**: Run scheduler in background for automated daily checks

## 📝 Next Steps

1. Customize AI decision logic in `ai_decision.py`
2. Add more technical indicators
3. Implement risk management rules
4. Set up email/SMS alerts
5. Add backtesting capabilities

Happy Trading! 🥭📈


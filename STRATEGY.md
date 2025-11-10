# 30-Minute Momentum Trading Strategy

## Strategy Overview

This system implements an automated momentum trading strategy that:

1. **Analyzes** all stocks at 10:00 AM EST (30 minutes after market open at 9:30 AM)
2. **Identifies** stocks that have moved up by more than 2% from their opening price
3. **Purchases** all qualifying stocks using available buying power
4. **Sets** automatic stop-loss orders at 1% below purchase price

## How It Works

### Step 1: Market Open Analysis (10:00 AM EST)

At exactly 10:00 AM EST (30 minutes after the market opens at 9:30 AM), the system:

- Loads all 7,000+ stocks from `Stock_list.csv`
- For each stock, retrieves:
  - Opening price at 9:30 AM EST
  - Current price at 10:00 AM EST
- Calculates the percentage change: `((current_price - open_price) / open_price) * 100`

### Step 2: Stock Selection

Stocks that qualify for purchase:
- Must have gained **more than 2%** from opening price
- Must have valid price data available
- Must be tradeable on Alpaca Markets

### Step 3: Automatic Purchasing

For all qualifying stocks:

1. **Position Sizing**: 
   - Uses 95% of available buying power
   - Distributes evenly across all qualifying stocks
   - Calculates: `shares = (available_cash / num_stocks) / stock_price`

2. **Order Execution**:
   - Places market orders immediately
   - Waits for order confirmation
   - Records purchase price

3. **Stop-Loss Setup**:
   - Calculates stop-loss price: `purchase_price * 0.99` (1% below)
   - Places stop-loss order with GTC (Good Till Cancelled)
   - Order automatically executes if price drops to stop-loss level

## Example Execution

```
Market opens: 9:30 AM EST
Strategy runs: 10:00 AM EST

Stock Analysis:
- AAPL: Open $150.00 → Current $153.50 (2.33% gain) ✅ QUALIFIES
- MSFT: Open $300.00 → Current $304.00 (1.33% gain) ❌ Does not qualify
- TSLA: Open $200.00 → Current $205.00 (2.50% gain) ✅ QUALIFIES

Purchasing:
- Buy 10 shares of AAPL at $153.50 = $1,535.00
- Set stop-loss at $152.00 (1% below)
- Buy 10 shares of TSLA at $205.00 = $2,050.00
- Set stop-loss at $202.95 (1% below)
```

## Risk Management

### Stop-Loss Protection
- Every purchase automatically gets a 1% stop-loss
- Protects against sudden downturns
- Stop-loss orders are "Good Till Cancelled" (GTC)

### Position Sizing
- Never uses 100% of buying power (uses 95%)
- Distributes risk across multiple stocks
- Prevents over-concentration in single positions

### Market Hours
- Only executes during market hours
- Runs at exact time (10:00 AM EST)
- Handles market holidays gracefully

## Configuration

### Strategy Parameters

In `trading_strategy.py`:

```python
self.momentum_threshold = 2.0  # Minimum 2% gain required
self.stop_loss_percent = 1.0  # 1% stop-loss below purchase price
```

### Schedule

In `scheduler.py`:

```python
schedule.every().day.at("10:00").do(execute_strategy)
```

## Manual Execution

### Test Strategy (Analyze Only)

```python
from trading_strategy import MomentumStrategy

strategy = MomentumStrategy()
qualifying, all_results = strategy.analyze_all_stocks()
print(f"Found {len(qualifying)} qualifying stocks")
```

### Execute Strategy

```python
from trading_strategy import MomentumStrategy

strategy = MomentumStrategy()
result = strategy.execute_daily_strategy()
print(f"Purchased {result['purchased_count']} stocks")
```

### Via API

```bash
# Analyze stocks (no purchase)
curl -X POST http://localhost:5000/api/strategy/analyze

# Execute full strategy (purchases stocks)
curl -X POST http://localhost:5000/api/strategy/execute
```

## Monitoring

### Check Positions

```python
from alpaca_client import AlpacaClient

client = AlpacaClient()
positions = client.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']}")
```

### View Stop-Loss Orders

```python
orders = client.get_orders(status='all')
stop_losses = [o for o in orders if o['order_type'] == 'stop']
```

## Performance Tracking

The system tracks:
- Number of qualifying stocks each day
- Number of stocks purchased
- Total invested amount
- Stop-loss orders placed
- All trades in database

## Important Notes

⚠️ **Paper Trading**: This system uses Alpaca's paper trading environment by default. No real money is at risk.

⚠️ **Market Conditions**: Strategy performance depends on market conditions. Not all days will have qualifying stocks.

⚠️ **Execution Time**: The strategy must run at exactly 10:00 AM EST. Earlier or later execution may affect results.

⚠️ **Data Availability**: Some stocks may not have intraday data available. The system handles these gracefully.

## Troubleshooting

### No Qualifying Stocks
- Normal on low-volatility days
- Check market conditions
- Verify data is available for stocks

### Purchase Failures
- Check buying power
- Verify stock is tradeable
- Check for market halts

### Stop-Loss Not Setting
- Verify order was placed successfully
- Check Alpaca account for stop-loss orders
- Review error logs

## Future Enhancements

- [ ] Volume filters (minimum volume requirement)
- [ ] Market cap filters
- [ ] Sector diversification
- [ ] Performance analytics
- [ ] Email/SMS alerts
- [ ] Backtesting capabilities

---

**Strategy runs automatically daily at 10:00 AM EST** 🚀


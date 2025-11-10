"""
30-Minute Momentum Strategy:
1. Check stocks at 10:00 AM (30 minutes after market open at 9:30 AM)
2. Identify stocks that moved up >2% from opening price
3. Purchase all qualifying stocks
4. Set stop-loss orders at 1% below purchase price
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
from alpaca_client import AlpacaClient
from database import StockPrice, Position, Trade, SessionLocal
from config import Config
import time
from alpaca.trade.requests import StopLossRequest, MarketOrderRequest
from alpaca.trade.enums import OrderSide, TimeInForce, OrderType

class MomentumStrategy:
    def __init__(self):
        self.alpaca = AlpacaClient()
        self.est = pytz.timezone(Config.STOCK_CHECK_TIMEZONE)
        self.momentum_threshold = 2.0  # 2% minimum gain
        self.stop_loss_percent = 1.0  # 1% stop loss
        
    def load_stock_list(self):
        """Load stock tickers from CSV file"""
        try:
            df = pd.read_csv(Config.STOCK_LIST_FILE)
            tickers = df['Ticker'].dropna().unique().tolist()
            tickers = [t for t in tickers if isinstance(t, str) and len(t) > 0]
            return tickers
        except Exception as e:
            print(f"Error loading stock list: {e}")
            return []
    
    def get_market_open_price(self, ticker):
        """Get the opening price at 9:30 AM EST"""
        try:
            stock = yf.Ticker(ticker)
            today = datetime.now(self.est).date()
            
            # Try to get intraday data (1-minute intervals)
            try:
                hist = stock.history(period="1d", interval="1m")
                
                if not hist.empty:
                    hist.index = pd.to_datetime(hist.index)
                    # Convert to EST timezone
                    hist.index = hist.index.tz_convert(self.est)
                    today_data = hist[hist.index.date == today]
                    
                    if not today_data.empty:
                        # Find the first price after 9:30 AM EST
                        market_open_time = today_data.index[0].replace(hour=9, minute=30, second=0, microsecond=0)
                        open_data = today_data[today_data.index >= market_open_time]
                        
                        if not open_data.empty:
                            return float(open_data.iloc[0]['Open'])
                        # If no data after 9:30, use first available
                        return float(today_data.iloc[0]['Open'])
                
            except Exception as e:
                pass
            
            # Fallback: use 5-minute intervals
            try:
                hist = stock.history(period="1d", interval="5m")
                if not hist.empty:
                    hist.index = pd.to_datetime(hist.index)
                    hist.index = hist.index.tz_convert(self.est)
                    today_data = hist[hist.index.date == today]
                    if not today_data.empty:
                        return float(today_data.iloc[0]['Open'])
            except Exception as e:
                pass
            
            # Last resort: use previous close
            try:
                info = stock.info
                prev_close = info.get('previousClose')
                if prev_close:
                    return float(prev_close)
            except:
                pass
            
            return None
                
        except Exception as e:
            print(f"Error getting open price for {ticker}: {e}")
            return None
    
    def get_current_price(self, ticker):
        """Get current price at 10:00 AM (30 min after market open)"""
        try:
            stock = yf.Ticker(ticker)
            today = datetime.now(self.est).date()
            
            # Try to get intraday data for current price
            try:
                hist = stock.history(period="1d", interval="1m")
                if not hist.empty:
                    hist.index = pd.to_datetime(hist.index)
                    hist.index = hist.index.tz_convert(self.est)
                    today_data = hist[hist.index.date == today]
                    
                    if not today_data.empty:
                        # Get price closest to 10:00 AM
                        target_time = today_data.index[0].replace(hour=10, minute=0, second=0, microsecond=0)
                        closest_data = today_data[today_data.index <= target_time]
                        
                        if not closest_data.empty:
                            return float(closest_data.iloc[-1]['Close'])
                        # Use latest available
                        return float(today_data.iloc[-1]['Close'])
            except:
                pass
            
            # Fallback: use info API
            try:
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if current_price:
                    return float(current_price)
            except:
                pass
            
            # Last resort: use latest history
            try:
                hist = stock.history(period="1d", interval="5m")
                if not hist.empty:
                    return float(hist.iloc[-1]['Close'])
            except:
                pass
            
            return None
        except Exception as e:
            print(f"Error getting current price for {ticker}: {e}")
            return None
    
    def calculate_momentum(self, ticker):
        """Calculate price movement from open to current (30 min after open)"""
        open_price = self.get_market_open_price(ticker)
        current_price = self.get_current_price(ticker)
        
        if not open_price or not current_price:
            return None
        
        if open_price == 0:
            return None
        
        change_percent = ((current_price - open_price) / open_price) * 100
        
        return {
            'ticker': ticker,
            'open_price': open_price,
            'current_price': current_price,
            'change_percent': change_percent,
            'qualifies': change_percent > self.momentum_threshold
        }
    
    def analyze_all_stocks(self):
        """Analyze all stocks to find those with >2% gain after 30 minutes"""
        tickers = self.load_stock_list()
        print(f"Analyzing {len(tickers)} stocks for 30-minute momentum...")
        
        qualifying_stocks = []
        results = []
        
        for i, ticker in enumerate(tickers):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(tickers)} stocks analyzed")
            
            momentum_data = self.calculate_momentum(ticker)
            
            if momentum_data:
                results.append(momentum_data)
                
                if momentum_data['qualifies']:
                    qualifying_stocks.append(momentum_data)
                    print(f"✅ {ticker}: {momentum_data['change_percent']:.2f}% gain")
            
            # Rate limiting
            time.sleep(0.1)
        
        print(f"\nFound {len(qualifying_stocks)} stocks with >{self.momentum_threshold}% gain")
        return qualifying_stocks, results
    
    def close_all_positions(self):
        """Close all open positions before starting new day trades"""
        print("\n" + "=" * 60)
        print("🔄 Closing All Existing Positions")
        print("=" * 60)
        
        positions = self.alpaca.get_positions()
        
        if not positions:
            print("No existing positions to close.")
            return {'closed': 0, 'errors': 0}
        
        print(f"Found {len(positions)} open positions to close...")
        
        closed_count = 0
        error_count = 0
        
        for pos in positions:
            symbol = pos['symbol']
            qty = int(pos['qty'])
            
            print(f"\n📤 Closing {qty} shares of {symbol}...")
            
            try:
                # Place market sell order
                order = self.alpaca.place_market_order(symbol, qty, 'sell')
                
                if order:
                    print(f"   ✅ Successfully closed {symbol}")
                    closed_count += 1
                else:
                    print(f"   ❌ Failed to close {symbol}")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error closing {symbol}: {e}")
                error_count += 1
            
            # Small delay between orders
            time.sleep(0.5)
        
        print(f"\n✅ Closed {closed_count} positions")
        if error_count > 0:
            print(f"⚠️  {error_count} positions had errors")
        
        # Wait a moment for orders to settle
        print("\n⏳ Waiting for orders to settle...")
        time.sleep(2)
        
        return {'closed': closed_count, 'errors': error_count}
    
    def calculate_position_size(self, account_balance, num_stocks, price_per_share):
        """Calculate how many shares to buy for each stock"""
        if num_stocks == 0 or account_balance <= 0:
            return 0
        
        # Use 100% of buying power for maximum capital utilization
        available_cash = account_balance
        
        # Distribute evenly across all qualifying stocks
        cash_per_stock = available_cash / num_stocks
        
        # Calculate shares (round down to whole shares)
        shares = int(cash_per_stock / price_per_share)
        
        return max(1, shares)  # At least 1 share
    
    def purchase_stocks(self, qualifying_stocks):
        """Purchase all qualifying stocks using 100% of available funds"""
        if not qualifying_stocks:
            print("No qualifying stocks to purchase")
            return []
        
        # Get account balance
        account = self.alpaca.get_account()
        if not account:
            print("Error: Could not get account information")
            return []
        
        initial_buying_power = account['buying_power']
        print(f"\nAvailable buying power: ${initial_buying_power:,.2f}")
        print(f"Using 100% of available funds for maximum capital utilization")
        
        # Pre-calculate all position sizes based on initial buying power
        num_stocks = len(qualifying_stocks)
        position_plans = []
        total_planned_cost = 0
        
        for stock_data in qualifying_stocks:
            ticker = stock_data['ticker']
            current_price = stock_data['current_price']
            
            # Calculate shares to buy
            shares = self.calculate_position_size(initial_buying_power, num_stocks, current_price)
            
            # Calculate cost
            cost = shares * current_price
            total_planned_cost += cost
            
            position_plans.append({
                'ticker': ticker,
                'shares': shares,
                'estimated_price': current_price,
                'estimated_cost': cost
            })
        
        print(f"\n📊 Position Plan:")
        print(f"   Stocks to purchase: {num_stocks}")
        print(f"   Total planned investment: ${total_planned_cost:,.2f}")
        print(f"   Capital utilization: {(total_planned_cost / initial_buying_power * 100):.1f}%")
        
        # Execute purchases
        purchases = []
        remaining_buying_power = initial_buying_power
        
        for plan in position_plans:
            ticker = plan['ticker']
            shares = plan['shares']
            estimated_price = plan['estimated_price']
            estimated_cost = plan['estimated_cost']
            
            if estimated_cost > remaining_buying_power:
                print(f"\n⚠️  Insufficient funds for {ticker}. Skipping...")
                print(f"   Needed: ${estimated_cost:.2f}, Available: ${remaining_buying_power:.2f}")
                continue
            
            print(f"\n📈 Purchasing {shares} shares of {ticker} at ~${estimated_price:.2f}")
            print(f"   Estimated cost: ${estimated_cost:.2f}")
            
            try:
                # Place market order
                order = self.alpaca.place_market_order(ticker, shares, 'buy')
                
                if order:
                    purchase_price = float(order.get('filled_avg_price') or estimated_price)
                    actual_cost = shares * purchase_price
                    
                    # Set stop-loss order
                    stop_loss_price = purchase_price * (1 - self.stop_loss_percent / 100)
                    stop_loss_set = self.set_stop_loss(ticker, shares, stop_loss_price)
                    
                    purchases.append({
                        'ticker': ticker,
                        'shares': shares,
                        'purchase_price': purchase_price,
                        'stop_loss_price': stop_loss_price,
                        'order_id': order.get('id'),
                        'stop_loss_set': stop_loss_set,
                        'actual_cost': actual_cost
                    })
                    
                    remaining_buying_power -= actual_cost
                    print(f"   ✅ Purchase successful! Price: ${purchase_price:.2f}, Stop-loss: ${stop_loss_price:.2f}")
                    print(f"   Remaining buying power: ${remaining_buying_power:,.2f}")
                else:
                    print(f"   ❌ Purchase failed for {ticker}")
                    
            except Exception as e:
                print(f"   ❌ Error purchasing {ticker}: {e}")
            
            # Small delay between orders
            time.sleep(0.5)
        
        return purchases
    
    def set_stop_loss(self, symbol, qty, stop_price):
        """Set a stop-loss order at 1% below purchase price"""
        try:
            # Use AlpacaClient's stop-loss method
            order = self.alpaca.place_stop_loss_order(symbol, qty, stop_price)
            
            if order:
                # Save to database
                db = SessionLocal()
                try:
                    trade = Trade(
                        ticker=symbol,
                        action='stop_loss',
                        quantity=qty,
                        price=stop_price,
                        timestamp=datetime.utcnow()
                    )
                    db.add(trade)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(f"Error saving stop-loss to database: {e}")
                finally:
                    db.close()
                
                return True
            return False
        except Exception as e:
            print(f"Error setting stop-loss for {symbol}: {e}")
            return False
    
    def execute_daily_strategy(self):
        """Execute the complete daily trading strategy"""
        print("=" * 60)
        print("🚀 Starting 30-Minute Momentum Strategy")
        print("=" * 60)
        print(f"Time: {datetime.now(self.est).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print()
        
        # Step 0: Close all existing positions first
        close_result = self.close_all_positions()
        
        # Step 1: Analyze all stocks
        qualifying_stocks, all_results = self.analyze_all_stocks()
        
        if not qualifying_stocks:
            print("\n❌ No stocks qualify for purchase today")
            return {
                'success': False,
                'message': 'No qualifying stocks found',
                'qualifying_count': 0,
                'positions_closed': close_result['closed'],
                'purchases': []
            }
        
        # Step 2: Purchase qualifying stocks
        print(f"\n💰 Purchasing {len(qualifying_stocks)} qualifying stocks...")
        purchases = self.purchase_stocks(qualifying_stocks)
        
        # Step 3: Summary
        print("\n" + "=" * 60)
        print("📊 Strategy Execution Summary")
        print("=" * 60)
        print(f"Positions closed: {close_result['closed']}")
        print(f"Stocks analyzed: {len(all_results)}")
        print(f"Stocks qualifying (>2% gain): {len(qualifying_stocks)}")
        print(f"Stocks purchased: {len(purchases)}")
        print(f"Stop-loss orders set: {sum(1 for p in purchases if p['stop_loss_set'])}")
        
        total_invested = sum(p['shares'] * p['purchase_price'] for p in purchases)
        print(f"Total invested: ${total_invested:,.2f}")
        
        # Get final account balance
        account = self.alpaca.get_account()
        if account:
            print(f"Remaining buying power: ${account['buying_power']:,.2f}")
            utilization = (total_invested / (total_invested + account['buying_power'])) * 100 if (total_invested + account['buying_power']) > 0 else 0
            print(f"Capital utilization: {utilization:.1f}%")
        
        return {
            'success': True,
            'positions_closed': close_result['closed'],
            'qualifying_count': len(qualifying_stocks),
            'purchased_count': len(purchases),
            'purchases': purchases,
            'total_invested': total_invested,
            'capital_utilization': utilization if account else 0
        }

if __name__ == "__main__":
    strategy = MomentumStrategy()
    result = strategy.execute_daily_strategy()
    print(f"\nStrategy execution completed: {result['success']}")


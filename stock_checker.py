import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from database import StockPrice, SessionLocal
from config import Config
import time

class StockChecker:
    def __init__(self):
        self.est = pytz.timezone(Config.STOCK_CHECK_TIMEZONE)
        
    def load_stock_list(self):
        """Load stock tickers from CSV file"""
        try:
            df = pd.read_csv(Config.STOCK_LIST_FILE)
            tickers = df['Ticker'].dropna().unique().tolist()
            # Filter out invalid tickers
            tickers = [t for t in tickers if isinstance(t, str) and len(t) > 0]
            return tickers
        except Exception as e:
            print(f"Error loading stock list: {e}")
            return []
    
    def get_stock_price(self, ticker):
        """Get current price for a single stock"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try to get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
            if current_price:
                # Get additional data
                hist = stock.history(period="2d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    previous = hist.iloc[-2] if len(hist) > 1 else latest
                    
                    change = float(latest['Close']) - float(previous['Close'])
                    change_percent = (change / float(previous['Close'])) * 100 if float(previous['Close']) != 0 else 0
                    volume = int(latest['Volume']) if 'Volume' in latest else None
                    
                    return {
                        'ticker': ticker,
                        'price': float(current_price),
                        'volume': volume,
                        'change': change,
                        'change_percent': change_percent
                    }
            
            return None
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None
    
    def check_all_stocks(self):
        """Check prices for all stocks in the list"""
        tickers = self.load_stock_list()
        print(f"Checking prices for {len(tickers)} stocks...")
        
        results = []
        db = SessionLocal()
        
        try:
            for i, ticker in enumerate(tickers):
                if i % 100 == 0:
                    print(f"Progress: {i}/{len(tickers)} stocks checked")
                
                price_data = self.get_stock_price(ticker)
                
                if price_data:
                    # Save to database
                    stock_price = StockPrice(
                        ticker=price_data['ticker'],
                        price=price_data['price'],
                        volume=price_data.get('volume'),
                        change=price_data.get('change'),
                        change_percent=price_data.get('change_percent'),
                        timestamp=datetime.utcnow()
                    )
                    db.add(stock_price)
                    results.append(price_data)
                
                # Rate limiting to avoid API issues
                time.sleep(0.1)
            
            db.commit()
            print(f"Successfully checked {len(results)} stocks")
            return results
            
        except Exception as e:
            db.rollback()
            print(f"Error checking stocks: {e}")
            return results
        finally:
            db.close()
    
    def get_latest_prices(self, limit=100):
        """Get latest prices from database"""
        db = SessionLocal()
        try:
            prices = db.query(StockPrice).order_by(StockPrice.timestamp.desc()).limit(limit).all()
            return [p.to_dict() for p in prices]
        finally:
            db.close()

if __name__ == "__main__":
    checker = StockChecker()
    results = checker.check_all_stocks()
    print(f"Checked {len(results)} stocks")


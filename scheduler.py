import schedule
import time
import pytz
from datetime import datetime
from trading_strategy import MomentumStrategy
from config import Config

class Scheduler:
    def __init__(self):
        self.strategy = MomentumStrategy()
        self.est = pytz.timezone(Config.STOCK_CHECK_TIMEZONE)
    
    def execute_trading_strategy_job(self):
        """Job to execute the 30-minute momentum strategy at 10 AM EST"""
        current_time = datetime.now(self.est)
        print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}] Starting 30-Minute Momentum Strategy...")
        
        try:
            result = self.strategy.execute_daily_strategy()
            
            if result['success']:
                print(f"[{datetime.now()}] Strategy executed successfully!")
                print(f"  - Qualifying stocks: {result['qualifying_count']}")
                print(f"  - Stocks purchased: {result['purchased_count']}")
                print(f"  - Total invested: ${result.get('total_invested', 0):,.2f}")
            else:
                print(f"[{datetime.now()}] Strategy completed: {result.get('message', 'No action taken')}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error executing trading strategy: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the scheduler - 100% AUTONOMOUS"""
        # Schedule strategy execution at 10:00 AM EST daily (30 min after market open)
        # Market opens at 9:30 AM EST, so 10:00 AM is exactly 30 minutes after
        schedule.every().day.at("10:00").do(self.execute_trading_strategy_job)
        
        print("=" * 60)
        print("🚀 MangoTrades V3 - 30-Minute Momentum Strategy Scheduler")
        print("=" * 60)
        print("✅ 100% AUTONOMOUS - No manual intervention required")
        print("Strategy will execute daily at 10:00 AM EST")
        print("(30 minutes after market open at 9:30 AM EST)")
        print()
        print("Strategy Details:")
        print("  1. Closes ALL existing positions")
        print("  2. Analyzes all stocks for >2% gain after 30 minutes")
        print("  3. Purchases ALL qualifying stocks (100% of funds)")
        print("  4. Sets 1% stop-loss on all purchases")
        print()
        print("💰 Uses 100% of available buying power each day")
        print("🔄 Sells all positions before new purchases")
        print("🤖 Fully automated - runs every trading day")
        print()
        print("Scheduler is running...")
        print("=" * 60)
        
        # Run scheduler - infinite loop for 100% autonomy
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()


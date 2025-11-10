# MangoTrades V3 - System Overview

## 🎯 System Architecture

### Core Components

1. **Stock Checker** (`stock_checker.py`)
   - Uses yfinance to fetch real-time stock prices
   - Processes 7,000+ stocks from CSV file
   - Stores prices in database with timestamps
   - Includes rate limiting to avoid API issues

2. **Alpaca Client** (`alpaca_client.py`)
   - Integrates with Alpaca Markets paper trading API
   - Handles market and limit orders
   - Manages positions and trades
   - Syncs with local database

3. **AI Decision Maker** (`ai_decision.py`)
   - Analyzes stocks using technical indicators
   - Generates buy/sell/hold signals
   - Uses RSI, MACD, SMA, and momentum indicators
   - Calculates confidence scores for each signal

4. **Scheduler** (`scheduler.py`)
   - Runs stock checks at 10:00 AM EST daily
   - Generates AI signals at 10:30 AM EST daily
   - Uses Python's schedule library
   - Handles timezone conversions

5. **Flask API** (`app.py`)
   - RESTful API for dashboard and external access
   - Endpoints for trading, positions, signals, and prices
   - CORS enabled for web access
   - Serves the dashboard HTML

6. **Database** (`database.py`)
   - SQLite database for local storage
   - Tables: stocks, stock_prices, positions, trades, ai_signals
   - SQLAlchemy ORM for easy data access

7. **Dashboard** (`static/index.html`)
   - Modern, responsive web interface
   - Real-time portfolio updates
   - Trade placement interface
   - Signal and price visualization

## 📊 Data Flow

```
Stock List CSV → Stock Checker → Database → Dashboard
                                      ↓
                              AI Decision Maker
                                      ↓
                              Alpaca API → Paper Trading
```

## 🔄 Daily Workflow

1. **10:00 AM EST**: Scheduler triggers stock check
   - Reads all tickers from CSV
   - Fetches prices using yfinance
   - Stores in database

2. **10:30 AM EST**: AI signal generation
   - Analyzes recent price data
   - Calculates technical indicators
   - Generates trading signals
   - Stores signals in database

3. **User Actions**: Throughout the day
   - View portfolio and positions
   - Place trades via dashboard
   - View AI signals
   - Check latest prices

## 🗄️ Database Schema

### stocks
- id, ticker, company_name, created_at

### stock_prices
- id, ticker, price, volume, change, change_percent, timestamp

### positions
- id, ticker, quantity, entry_price, current_price, position_type, status, opened_at, closed_at

### trades
- id, ticker, action, quantity, price, position_id, timestamp

### ai_signals
- id, ticker, signal_type, confidence, reasoning, timestamp

## 🔐 Security Features

- API keys stored in `.env` file (not committed)
- Paper trading only (no real money)
- Input validation on all API endpoints
- SQL injection protection via SQLAlchemy ORM

## 📈 Trading Features

### Supported Operations
- ✅ Market orders (immediate execution)
- ✅ Limit orders (price-based execution)
- ✅ Long positions (buy and hold)
- ✅ Short positions (sell first, buy later)
- ✅ Position tracking
- ✅ P&L calculation

### AI Signal Types
- **Buy**: Confidence > 60% (bullish indicators)
- **Sell**: Confidence < 40% (bearish indicators)
- **Hold**: 40% ≤ Confidence ≤ 60% (neutral)

## 🛠️ Technical Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Stock Data**: yfinance
- **Trading API**: Alpaca Markets
- **Scheduling**: schedule library
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI/ML**: scikit-learn (for future enhancements)

## 🚀 Performance Considerations

- **Rate Limiting**: 0.1s delay between stock checks
- **Batch Processing**: Processes stocks in batches
- **Database Indexing**: Ticker and timestamp indexes
- **Caching**: Recent prices cached in memory
- **Async Ready**: Can be converted to async for better performance

## 📝 Configuration

All settings in `config.py`:
- Alpaca API credentials
- Database URL
- Stock check schedule time
- Stock list file path

## 🔮 Future Enhancements

1. **Real-time Updates**: WebSocket for live price feeds
2. **Advanced ML**: Deep learning models for predictions
3. **Backtesting**: Historical strategy testing
4. **Risk Management**: Stop-loss, take-profit orders
5. **Alerts**: Email/SMS notifications
6. **Multi-strategy**: Support multiple trading strategies
7. **Analytics**: Performance metrics and charts
8. **Paper to Live**: Easy transition to live trading

## 📚 File Structure

```
MangoTrades V3/
├── app.py              # Flask API server
├── config.py           # Configuration
├── database.py         # Database models
├── stock_checker.py    # Stock price fetching
├── alpaca_client.py    # Trading API client
├── ai_decision.py      # AI signal generation
├── scheduler.py        # Automated scheduling
├── run_scheduler.py    # Scheduler runner
├── start.sh           # Startup script
├── requirements.txt    # Dependencies
├── .env               # API keys (not in git)
├── .gitignore         # Git ignore rules
├── README.md          # Main documentation
├── QUICKSTART.md      # Quick start guide
├── SYSTEM_OVERVIEW.md # This file
├── Stock_list.csv     # 7,000+ stock tickers
├── static/
│   └── index.html     # Web dashboard
└── mangotrades.db     # SQLite database (created on first run)
```

## ✅ System Status

All core features implemented and tested:
- ✅ Stock price checking (7,000+ stocks)
- ✅ Alpaca paper trading integration
- ✅ AI signal generation
- ✅ Portfolio management
- ✅ Web dashboard
- ✅ Automated scheduling
- ✅ Database persistence
- ✅ RESTful API

## 🎓 Learning Resources

- Alpaca API Docs: https://alpaca.markets/docs/
- yfinance Docs: https://github.com/ranaroussi/yfinance
- Flask Docs: https://flask.palletsprojects.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/

---

**System is ready for use!** 🥭📈

Start with: `python3 app.py` and visit http://localhost:5000


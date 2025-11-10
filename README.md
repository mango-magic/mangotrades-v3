# MangoTrades V3 - AI-Powered Stock Trading Platform

A comprehensive stock trading system that checks 7,000+ stocks daily at 10 AM EST and provides AI-powered trading signals with portfolio management capabilities.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## Features

- 🚀 **30-Minute Momentum Strategy**: Automatically identifies and purchases stocks with >2% gain after 30 minutes of market open
- 💰 **Automatic Purchasing**: Buys all qualifying stocks using available buying power
- 🛡️ **Stop-Loss Protection**: Automatically sets 1% stop-loss on all purchases
- 📊 **Stock Analysis**: Analyzes 7,000+ stocks daily at 10:00 AM EST (30 min after market open)
- 💹 **Paper Trading**: Full integration with Alpaca Markets paper trading API
- 📈 **Portfolio Management**: Track positions, trades, and portfolio performance
- 🎨 **Modern Dashboard**: Beautiful web interface for managing your portfolio
- ⏰ **Automated Scheduling**: Runs strategy automatically each trading day
- ☁️ **Cloud Ready**: Deploy to Render with one click

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from database import init_db; init_db()"

# Start the server
python3 app.py
```

Then open: **http://localhost:5000**

### Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

Required keys:
- `ALPACA_API_KEY` - Your Alpaca API key
- `ALPACA_SECRET_KEY` - Your Alpaca secret key
- `GEMINI_API_KEY` - Your Google Gemini API key (optional but recommended)

### 3. Initialize Database

The database will be created automatically on first run. To manually initialize:

```python
from database import init_db
init_db()
```

## Usage

### Start the API Server

```bash
python3 app.py
```

The API will be available at `http://localhost:5000`

### Access the Dashboard

Open `http://localhost:5000` in your web browser.

### Run the Scheduler

To start automatic stock checking at 10 AM EST:

```bash
python3 run_scheduler.py
```

### Manual Stock Check

```python
from stock_checker import StockChecker

checker = StockChecker()
results = checker.check_all_stocks()
print(f"Checked {len(results)} stocks")
```

### Generate AI Signals

```python
from ai_decision import AIDecisionMaker

ai = AIDecisionMaker()
signal = ai.generate_signal("AAPL")
print(signal)
```

## API Endpoints

### Account & Portfolio
- `GET /api/account` - Get account information
- `GET /api/portfolio/summary` - Get portfolio summary
- `GET /api/positions` - Get all open positions
- `GET /api/positions/<ticker>` - Get position for specific ticker

### Trading
- `POST /api/trades` - Place a new trade
- `GET /api/trades` - Get all trades
- `GET /api/orders` - Get all orders
- `DELETE /api/orders/<order_id>` - Cancel an order

### Stocks
- `GET /api/stocks/prices` - Get latest stock prices
- `POST /api/stocks/check` - Manually trigger stock check

### AI Signals
- `GET /api/ai/signals` - Get AI trading signals
- `POST /api/ai/signals/generate` - Generate new signals

## Project Structure

```
MangoTrades V3/
├── app.py                 # Flask API server
├── config.py             # Configuration settings
├── database.py           # Database models
├── stock_checker.py      # Stock price checking with yfinance
├── alpaca_client.py      # Alpaca API integration
├── ai_decision.py        # AI trading signal generation (with Gemini)
├── scheduler.py           # Automated scheduling
├── run_scheduler.py      # Scheduler runner
├── requirements.txt      # Python dependencies
├── Procfile              # Render process file
├── render.yaml           # Render deployment config
├── runtime.txt           # Python version
├── Stock_list.csv        # List of 7,000+ stocks
├── static/
│   └── index.html        # Web dashboard
├── README.md             # This file
├── DEPLOYMENT.md         # Deployment guide
├── QUICKSTART.md         # Quick start guide
└── GITHUB_SETUP.md       # GitHub setup guide
```

## Database Schema

- **stocks**: Stock ticker information
- **stock_prices**: Historical price data
- **positions**: Open and closed positions
- **trades**: Trade history
- **ai_signals**: AI-generated trading signals

## Trading Features

### Supported Order Types
- Market orders
- Limit orders

### Position Types
- Long positions
- Short positions (via sell orders)

### AI Signal Types
- Buy signals (confidence > 60%)
- Sell signals (confidence < 40%)
- Hold signals (40% ≤ confidence ≤ 60%)

## Technical Indicators Used

- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- SMA (Simple Moving Averages)
- Price momentum
- Volume analysis
- **Gemini AI Analysis** (when API key is configured)

## Trading Strategy

### 30-Minute Momentum Strategy

The system implements an automated momentum trading strategy:

1. **10:00 AM EST**: Analyzes all stocks for >2% gain from opening price (9:30 AM)
2. **Automatic Purchase**: Buys all qualifying stocks with available buying power
3. **Stop-Loss**: Sets 1% stop-loss orders on all purchases automatically

See [STRATEGY.md](STRATEGY.md) for detailed strategy documentation.

## Scheduling

The scheduler runs:
- **Strategy Execution**: Daily at 10:00 AM EST (30 minutes after market open)

## Deployment

### Render Deployment

1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Add environment variables in Render dashboard
5. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Security Notes

- Never commit `.env` file with real API keys
- Use paper trading for testing
- The system uses Alpaca's paper trading environment by default
- All secrets should be stored as environment variables

## Troubleshooting

### API Connection Issues
- Verify Alpaca API keys in `.env` or Render environment variables
- Check internet connection
- Ensure Alpaca paper trading account is active

### Stock Check Errors
- Some tickers may be invalid or delisted
- yfinance API has rate limits (system includes delays)
- Check logs for specific ticker errors

### Database Issues
- Delete `mangotrades.db` to reset database (local)
- On Render, use PostgreSQL database
- Ensure write permissions in project directory

### Gemini API Errors
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota/limits
- System will fall back to rule-based signals if Gemini unavailable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and personal use only. Always trade responsibly and understand the risks involved in stock trading.

## Support

For issues or questions:
- Check the logs in the console output
- Review error messages in the dashboard
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- See [QUICKSTART.md](QUICKSTART.md) for quick start guide

---

**Built with ❤️ for intelligent trading** 🥭📈

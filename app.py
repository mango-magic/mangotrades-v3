from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from database import init_db, get_db, StockPrice, Position, Trade, AISignal
from stock_checker import StockChecker
from alpaca_client import AlpacaClient
from ai_decision import AIDecisionMaker
from trading_strategy import MomentumStrategy
from datetime import datetime, timedelta
from sqlalchemy import func
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize components
stock_checker = StockChecker()
alpaca_client = AlpacaClient()
ai_decision = AIDecisionMaker()
momentum_strategy = MomentumStrategy()

# Initialize database
init_db()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/account', methods=['GET'])
def get_account():
    """Get Alpaca account information"""
    account = alpaca_client.get_account()
    if account:
        return jsonify(account)
    return jsonify({'error': 'Failed to get account info'}), 500

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get all positions"""
    db = next(get_db())
    try:
        positions = db.query(Position).filter_by(status='open').all()
        return jsonify([p.to_dict() for p in positions])
    finally:
        db.close()

@app.route('/api/positions/<ticker>', methods=['GET'])
def get_position(ticker):
    """Get position for a specific ticker"""
    db = next(get_db())
    try:
        position = db.query(Position).filter_by(ticker=ticker.upper(), status='open').first()
        if position:
            return jsonify(position.to_dict())
        return jsonify({'error': 'Position not found'}), 404
    finally:
        db.close()

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get all trades"""
    db = next(get_db())
    try:
        limit = request.args.get('limit', 100, type=int)
        trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
        return jsonify([t.to_dict() for t in trades])
    finally:
        db.close()

@app.route('/api/trades', methods=['POST'])
def create_trade():
    """Place a new trade"""
    data = request.json
    ticker = data.get('ticker', '').upper()
    quantity = data.get('quantity', 0)
    side = data.get('side', 'buy')  # 'buy' or 'sell'
    order_type = data.get('order_type', 'market')  # 'market' or 'limit'
    limit_price = data.get('limit_price')
    
    if not ticker or quantity <= 0:
        return jsonify({'error': 'Invalid ticker or quantity'}), 400
    
    try:
        if order_type == 'market':
            result = alpaca_client.place_market_order(ticker, quantity, side)
        else:
            if not limit_price:
                return jsonify({'error': 'Limit price required for limit orders'}), 400
            result = alpaca_client.place_limit_order(ticker, quantity, limit_price, side)
        
        if result:
            return jsonify(result)
        return jsonify({'error': 'Failed to place order'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/prices', methods=['GET'])
def get_stock_prices():
    """Get latest stock prices"""
    limit = request.args.get('limit', 100, type=int)
    ticker = request.args.get('ticker')
    
    db = next(get_db())
    try:
        query = db.query(StockPrice)
        
        if ticker:
            query = query.filter_by(ticker=ticker.upper())
        
        # Get latest price for each ticker
        if not ticker:
            subquery = db.query(
                StockPrice.ticker,
                func.max(StockPrice.timestamp).label('max_timestamp')
            ).group_by(StockPrice.ticker).subquery()
            
            prices = db.query(StockPrice).join(
                subquery,
                (StockPrice.ticker == subquery.c.ticker) &
                (StockPrice.timestamp == subquery.c.max_timestamp)
            ).order_by(StockPrice.timestamp.desc()).limit(limit).all()
        else:
            prices = query.order_by(StockPrice.timestamp.desc()).limit(limit).all()
        
        return jsonify([p.to_dict() for p in prices])
    finally:
        db.close()

@app.route('/api/stocks/check', methods=['POST'])
def check_stocks():
    """Manually trigger stock price check"""
    try:
        results = stock_checker.check_all_stocks()
        return jsonify({
            'success': True,
            'count': len(results),
            'message': f'Checked {len(results)} stocks'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/execute', methods=['POST'])
def execute_strategy():
    """Manually execute the 30-minute momentum strategy"""
    try:
        result = momentum_strategy.execute_daily_strategy()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/strategy/analyze', methods=['POST'])
def analyze_stocks():
    """Analyze stocks for momentum without purchasing"""
    try:
        qualifying_stocks, all_results = momentum_strategy.analyze_all_stocks()
        return jsonify({
            'success': True,
            'total_analyzed': len(all_results),
            'qualifying_count': len(qualifying_stocks),
            'qualifying_stocks': qualifying_stocks[:50],  # Limit to 50 for response
            'all_results': all_results[:100]  # Limit to 100 for response
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/ai/signals', methods=['GET'])
def get_ai_signals():
    """Get AI trading signals"""
    limit = request.args.get('limit', 100, type=int)
    ticker = request.args.get('ticker')
    signal_type = request.args.get('signal_type')  # 'buy', 'sell', 'hold'
    
    db = next(get_db())
    try:
        query = db.query(AISignal)
        
        if ticker:
            query = query.filter_by(ticker=ticker.upper())
        if signal_type:
            query = query.filter_by(signal_type=signal_type)
        
        signals = query.order_by(AISignal.timestamp.desc()).limit(limit).all()
        return jsonify([s.to_dict() for s in signals])
    finally:
        db.close()

@app.route('/api/ai/signals/generate', methods=['POST'])
def generate_signals():
    """Manually trigger AI signal generation"""
    data = request.json or {}
    ticker = data.get('ticker')
    limit = data.get('limit', 50)
    
    try:
        if ticker:
            signal = ai_decision.generate_signal(ticker)
            if signal:
                return jsonify(signal)
            return jsonify({'error': 'Failed to generate signal'}), 500
        else:
            tickers = stock_checker.load_stock_list()
            signals = ai_decision.generate_signals_for_stocks(tickers, limit=limit)
            return jsonify({
                'success': True,
                'count': len(signals),
                'signals': signals
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """Get portfolio summary"""
    db = next(get_db())
    try:
        # Get account info
        account = alpaca_client.get_account()
        
        # Get positions
        positions = db.query(Position).filter_by(status='open').all()
        
        total_unrealized_pnl = sum([p.calculate_unrealized_pnl() for p in positions])
        
        # Get recent trades
        recent_trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'account': account,
            'positions_count': len(positions),
            'total_unrealized_pnl': total_unrealized_pnl,
            'recent_trades': [t.to_dict() for t in recent_trades]
        })
    finally:
        db.close()

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    status = request.args.get('status', 'all')
    orders = alpaca_client.get_orders(status=status)
    return jsonify(orders)

@app.route('/api/orders/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order"""
    success = alpaca_client.cancel_order(order_id)
    if success:
        return jsonify({'success': True, 'message': 'Order cancelled'})
    return jsonify({'error': 'Failed to cancel order'}), 500

@app.route('/')
def index():
    """Serve the dashboard"""
    return send_file('static/index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = Config.FLASK_DEBUG
    print("Starting MangoTrades API server...")
    print(f"Dashboard will be available at http://localhost:{port}")
    print(f"API endpoints available at http://localhost:{port}/api")
    app.run(debug=debug, host='0.0.0.0', port=port)


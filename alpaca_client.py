from alpaca.trade.client import TradeClient
from alpaca.trade.requests import MarketOrderRequest, LimitOrderRequest, StopLossRequest
from alpaca.trade.enums import OrderSide, TimeInForce
from config import Config
from database import Position, Trade, SessionLocal
from datetime import datetime

class AlpacaClient:
    def __init__(self):
        self.client = TradeClient(
            api_key=Config.ALPACA_API_KEY,
            secret_key=Config.ALPACA_SECRET_KEY,
            base_url=Config.ALPACA_BASE_URL,
            paper=True
        )
    
    def get_account(self):
        """Get account information"""
        try:
            account = self.client.get_account()
            return {
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'day_trading_buying_power': float(account.day_trading_buying_power)
            }
        except Exception as e:
            print(f"Error getting account: {e}")
            return None
    
    def get_positions(self):
        """Get all open positions"""
        try:
            positions = self.client.list_positions()
            return [{
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc),
                'side': pos.side
            } for pos in positions]
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def place_market_order(self, symbol, qty, side='buy'):
        """Place a market order"""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.client.submit_order(order_data=order_data)
            
            # Save to database
            db = SessionLocal()
            try:
                trade = Trade(
                    ticker=symbol,
                    action=side,
                    quantity=qty,
                    price=float(order.filled_avg_price) if order.filled_avg_price else 0,
                    timestamp=datetime.utcnow()
                )
                db.add(trade)
                
                # Update or create position
                if side == 'buy':
                    position = db.query(Position).filter_by(
                        ticker=symbol,
                        status='open'
                    ).first()
                    
                    if position:
                        # Update existing position
                        total_qty = position.quantity + qty
                        total_cost = (position.entry_price * position.quantity) + (float(order.filled_avg_price) * qty)
                        position.entry_price = total_cost / total_qty
                        position.quantity = total_qty
                    else:
                        # Create new position
                        position = Position(
                            ticker=symbol,
                            quantity=qty,
                            entry_price=float(order.filled_avg_price) if order.filled_avg_price else 0,
                            position_type='long',
                            status='open'
                        )
                        db.add(position)
                else:  # sell
                    position = db.query(Position).filter_by(
                        ticker=symbol,
                        status='open'
                    ).first()
                    
                    if position:
                        position.quantity -= qty
                        if position.quantity <= 0:
                            position.status = 'closed'
                            position.closed_at = datetime.utcnow()
                    else:
                        # Position not in DB but exists in Alpaca - mark as closed
                        position = Position(
                            ticker=symbol,
                            quantity=qty,
                            entry_price=float(order.filled_avg_price) if order.filled_avg_price else 0,
                            position_type='long',
                            status='closed',
                            closed_at=datetime.utcnow()
                        )
                        db.add(position)
                
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error saving trade to database: {e}")
            finally:
                db.close()
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'filled_qty': float(order.filled_qty),
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'status': order.status,
                'side': order.side
            }
        except Exception as e:
            print(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, symbol, qty, limit_price, side='buy'):
        """Place a limit order"""
        try:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = self.client.submit_order(order_data=order_data)
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'limit_price': float(limit_price),
                'status': order.status,
                'side': order.side
            }
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        try:
            self.client.cancel_order_by_id(order_id)
            return True
        except Exception as e:
            print(f"Error canceling order: {e}")
            return False
    
    def place_stop_loss_order(self, symbol, qty, stop_price):
        """Place a stop-loss order"""
        try:
            stop_order = StopLossRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                stop_price=stop_price,
                time_in_force=TimeInForce.GTC
            )
            
            order = self.client.submit_order(order_data=stop_order)
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'stop_price': float(stop_price),
                'status': order.status,
                'side': order.side
            }
        except Exception as e:
            print(f"Error placing stop-loss order: {e}")
            return None
    
    def get_orders(self, status='all'):
        """Get orders"""
        try:
            orders = self.client.list_orders(status=status)
            return [{
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'filled_qty': float(order.filled_qty),
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'status': order.status,
                'side': order.side,
                'order_type': order.order_type,
                'time_in_force': order.time_in_force,
                'created_at': order.created_at.isoformat() if order.created_at else None
            } for order in orders]
        except Exception as e:
            print(f"Error getting orders: {e}")
            return []


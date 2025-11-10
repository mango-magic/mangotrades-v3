from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer)
    change = Column(Float)
    change_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'price': self.price,
            'volume': self.volume,
            'change': self.change,
            'change_percent': self.change_percent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    position_type = Column(String(10), nullable=False)  # 'long' or 'short'
    status = Column(String(20), default='open')  # 'open' or 'closed'
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'position_type': self.position_type,
            'status': self.status,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'unrealized_pnl': self.calculate_unrealized_pnl() if self.status == 'open' else None
        }
    
    def calculate_unrealized_pnl(self):
        if self.current_price and self.status == 'open':
            if self.position_type == 'long':
                return (self.current_price - self.entry_price) * self.quantity
            else:  # short
                return (self.entry_price - self.current_price) * self.quantity
        return 0

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    position_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'position_id': self.position_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AISignal(Base):
    __tablename__ = 'ai_signals'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    signal_type = Column(String(20), nullable=False)  # 'buy', 'sell', 'hold'
    confidence = Column(Float)  # 0.0 to 1.0
    reasoning = Column(String(1000))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# Database setup
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


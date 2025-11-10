import pandas as pd
import numpy as np
from database import StockPrice, AISignal, SessionLocal
from datetime import datetime, timedelta
import yfinance as yf
from config import Config

# Try to import scikit-learn (optional - may not be available on Python 3.13)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    RandomForestClassifier = None
    StandardScaler = None

# Try to import Gemini API
try:
    import google.generativeai as genai
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False

class AIDecisionMaker:
    def __init__(self):
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
        else:
            self.model = None
            self.scaler = None
            print("Warning: scikit-learn not available. Using technical indicators only.")
        self.is_trained = False
        self.use_gemini = GEMINI_AVAILABLE and Config.GEMINI_API_KEY
    
    def get_technical_indicators(self, ticker, period_days=30):
        """Get technical indicators for a stock"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{period_days}d")
            
            if hist.empty or len(hist) < 10:
                return None
            
            # Calculate indicators
            hist['SMA_5'] = hist['Close'].rolling(window=5).mean()
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['RSI'] = self.calculate_rsi(hist['Close'], 14)
            hist['MACD'], hist['MACD_signal'] = self.calculate_macd(hist['Close'])
            
            # Get latest values
            latest = hist.iloc[-1]
            
            return {
                'price': float(latest['Close']),
                'sma_5': float(latest['SMA_5']) if not pd.isna(latest['SMA_5']) else None,
                'sma_20': float(latest['SMA_20']) if not pd.isna(latest['SMA_20']) else None,
                'rsi': float(latest['RSI']) if not pd.isna(latest['RSI']) else None,
                'macd': float(latest['MACD']) if not pd.isna(latest['MACD']) else None,
                'macd_signal': float(latest['MACD_signal']) if not pd.isna(latest['MACD_signal']) else None,
                'volume': float(latest['Volume']),
                'price_change': float((latest['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close'] * 100) if len(hist) > 1 else 0
            }
        except Exception as e:
            print(f"Error getting technical indicators for {ticker}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def generate_signal(self, ticker):
        """Generate trading signal for a stock"""
        indicators = self.get_technical_indicators(ticker)
        
        if not indicators:
            return None
        
        # Simple rule-based system (can be enhanced with ML)
        signals = []
        confidence = 0.5
        
        # RSI signals
        if indicators['rsi']:
            if indicators['rsi'] < 30:
                signals.append("Oversold - Potential Buy")
                confidence += 0.2
            elif indicators['rsi'] > 70:
                signals.append("Overbought - Potential Sell")
                confidence -= 0.2
        
        # Moving average crossover
        if indicators['sma_5'] and indicators['sma_20']:
            if indicators['sma_5'] > indicators['sma_20']:
                signals.append("Bullish MA Crossover")
                confidence += 0.15
            else:
                signals.append("Bearish MA Crossover")
                confidence -= 0.15
        
        # MACD signals
        if indicators['macd'] and indicators['macd_signal']:
            if indicators['macd'] > indicators['macd_signal']:
                signals.append("Bullish MACD")
                confidence += 0.1
            else:
                signals.append("Bearish MACD")
                confidence -= 0.1
        
        # Price momentum
        if indicators['price_change']:
            if indicators['price_change'] > 2:
                signals.append("Strong Upward Momentum")
                confidence += 0.1
            elif indicators['price_change'] < -2:
                signals.append("Strong Downward Momentum")
                confidence -= 0.1
        
        # Determine signal type
        if confidence > 0.6:
            signal_type = 'buy'
        elif confidence < 0.4:
            signal_type = 'sell'
        else:
            signal_type = 'hold'
        
        confidence = max(0.0, min(1.0, abs(confidence)))
        reasoning = "; ".join(signals) if signals else "No strong signals"
        
        # Enhance with Gemini AI if available
        if self.use_gemini:
            gemini_reasoning = self.get_gemini_analysis(ticker, indicators, signals)
            if gemini_reasoning:
                reasoning += f" | AI Analysis: {gemini_reasoning}"
        
        # Save signal to database
        db = SessionLocal()
        try:
            ai_signal = AISignal(
                ticker=ticker,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.utcnow()
            )
            db.add(ai_signal)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving signal: {e}")
        finally:
            db.close()
        
        return {
            'ticker': ticker,
            'signal_type': signal_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': indicators
        }
    
    def generate_signals_for_stocks(self, tickers, limit=50):
        """Generate signals for multiple stocks"""
        results = []
        for i, ticker in enumerate(tickers[:limit]):
            if i % 10 == 0:
                print(f"Generating signals: {i}/{min(len(tickers), limit)}")
            
            signal = self.generate_signal(ticker)
            if signal:
                results.append(signal)
        
        return results
    
    def get_gemini_analysis(self, ticker, indicators, signals):
        """Get AI analysis from Gemini API"""
        if not self.use_gemini:
            return None
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analyze the stock {ticker} with the following technical indicators:
            - Current Price: ${indicators.get('price', 'N/A')}
            - RSI: {indicators.get('rsi', 'N/A')}
            - MACD: {indicators.get('macd', 'N/A')}
            - Price Change: {indicators.get('price_change', 'N/A')}%
            - Volume: {indicators.get('volume', 'N/A')}
            
            Current signals detected: {', '.join(signals) if signals else 'None'}
            
            Provide a brief trading recommendation (buy/sell/hold) with 1-2 sentence reasoning.
            Focus on risk assessment and market conditions.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error getting Gemini analysis: {e}")
            return None
    
    def get_recent_signals(self, limit=100):
        """Get recent AI signals from database"""
        db = SessionLocal()
        try:
            signals = db.query(AISignal).order_by(AISignal.timestamp.desc()).limit(limit).all()
            return [s.to_dict() for s in signals]
        finally:
            db.close()


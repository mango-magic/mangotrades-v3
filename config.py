import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # AI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    
    # Render Configuration
    RENDER_API_KEY = os.getenv('RENDER_API_KEY', '')
    
    # Database Configuration
    # Use PostgreSQL on Render, SQLite locally
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mangotrades.db')
    # Convert Render's postgres:// to sqlalchemy's postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Stock Check Schedule (10 AM EST)
    STOCK_CHECK_HOUR = 10
    STOCK_CHECK_MINUTE = 0
    STOCK_CHECK_TIMEZONE = 'America/New_York'
    
    # Stock List File
    STOCK_LIST_FILE = 'Stock_list.csv'
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'


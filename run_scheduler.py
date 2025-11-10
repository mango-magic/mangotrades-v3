#!/usr/bin/env python3
"""
Run the scheduler in a separate process
This will check stocks at 10 AM EST and generate AI signals at 10:30 AM EST
"""

from scheduler import Scheduler
from database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("Starting scheduler...")
    scheduler = Scheduler()
    scheduler.start()


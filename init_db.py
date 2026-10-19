"""
Database Initialization Script for Sales Data Analysis System
Run this script to create the 'sales_analysis' database and tables:
    python init_db.py
"""
import sys
from config import Config
from core.database import test_connection, init_db

def main():
    print("=" * 60)
    print("  Sales Data Analysis System - Database Initialization")
    print("=" * 60)
    print(f"Target Database Server: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"User:                   {Config.DB_USER}")
    print(f"Target Database:        {Config.DB_NAME}")
    print("-" * 60)

    print("\n[Step 1] Testing MySQL Connection...")
    status, msg = test_connection()
    if not status:
        print(f"\n[!] Connection Failed: {msg}\n")
        print("To fix this:")
        print("1. Ensure MySQL Server is running on your machine.")
        print("2. Open the '.env' file in this project folder.")
        print("3. Set your MySQL root password: DB_PASSWORD=your_password")
        print("4. Save '.env' and run 'python init_db.py' again.")
        print("=" * 60)
        sys.exit(1)

    print(f"[✓] MySQL Connected: {msg}")

    print("\n[Step 2] Initializing Database & Tables...")
    init_ok, init_msg = init_db()
    if init_ok:
        print(f"[✓] Success: {init_msg}")
        print("\nAll database tables ('products', 'sales') are ready to receive data!")
        print("=" * 60)
    else:
        print(f"\n[!] Initialization Failed: {init_msg}")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

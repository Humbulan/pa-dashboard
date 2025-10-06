import sqlite3
import datetime as dt
import random
from pathlib import Path

DB = Path(__file__).parent / "business.db"

def setup_business_tables():
    if DB.exists():
        DB.unlink()
    
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE email_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            sender_email TEXT,
            sender_name TEXT,
            subject TEXT,
            category TEXT,
            priority INTEGER DEFAULT 1,
            response_required BOOLEAN DEFAULT FALSE,
            response_time_hours REAL,
            sentiment_score REAL
        )
    """)
    con.execute("""
        CREATE TABLE website_traffic (
            date DATE PRIMARY KEY,
            visitors INTEGER DEFAULT 0,
            pageviews INTEGER DEFAULT 0,
            bounce_rate REAL DEFAULT 0,
            avg_session_duration REAL DEFAULT 0,
            conversion_rate REAL DEFAULT 0
        )
    """)
    con.execute("""
        CREATE TABLE business_metrics (
            date DATE PRIMARY KEY,
            revenue REAL DEFAULT 0,
            new_customers INTEGER DEFAULT 0,
            support_tickets INTEGER DEFAULT 0,
            social_mentions INTEGER DEFAULT 0,
            customer_satisfaction REAL DEFAULT 0
        )
    """)
    insert_sample_data(con)
    con.commit()
    con.close()
    print("✅ Humbu Store business database created!")

def insert_sample_data(con):
    base_date = dt.date.today() - dt.timedelta(days=90)
    email_categories = ["sales", "inquiry", "support", "partnership"]
    senders = ["customer@gmail.com", "client@company.co.za", "partner@business.com"]
    
    for i in range(90):
        current_date = base_date + dt.timedelta(days=i)
        for j in range(random.randint(5, 15)):
            con.execute(
                "INSERT INTO email_analytics (date, sender_email, subject, category, priority, response_time_hours) VALUES (?, ?, ?, ?, ?, ?)",
                (current_date, random.choice(senders), f"Business {random.choice(['Inquiry', 'Order'])}", random.choice(email_categories), random.randint(1, 3), random.uniform(1, 72))
            )
        con.execute(
            "INSERT INTO website_traffic (date, visitors, pageviews, bounce_rate, avg_session_duration, conversion_rate) VALUES (?, ?, ?, ?, ?, ?)",
            (current_date, random.randint(150, 400), random.randint(300, 1200), random.uniform(0.3, 0.6), random.uniform(120, 480), random.uniform(0.02, 0.08))
        )
        con.execute(
            "INSERT INTO business_metrics (date, revenue, new_customers, support_tickets, social_mentions, customer_satisfaction) VALUES (?, ?, ?, ?, ?, ?)",
            (current_date, random.uniform(800, 3000), random.randint(2, 8), random.randint(1, 5), random.randint(3, 15), random.uniform(4.0, 5.0))
        )

if __name__ == "__main__":
    setup_business_tables()

import sqlite3
import datetime as dt
import random
import os

DB = os.path.join(os.path.dirname(__file__), "business.db")

def append_today_data():
    con = sqlite3.connect(DB)
    today = dt.date.today()
    
    try:
        email_categories = ["sales", "inquiry", "support", "partnership"]
        senders = ["customer@gmail.com", "client@company.co.za", "partner@business.com"]
        
        for i in range(random.randint(3, 8)):
            con.execute(
                """INSERT OR REPLACE INTO email_analytics 
                (date, sender_email, subject, category, priority, response_time_hours)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    today,
                    random.choice(senders),
                    f"Business {random.choice(['Inquiry', 'Order', 'Support'])}",
                    random.choice(email_categories),
                    random.randint(1, 3),
                    random.uniform(1, 48)
                )
            )
        
        con.execute(
            """INSERT OR REPLACE INTO website_traffic 
            (date, visitors, pageviews, bounce_rate, avg_session_duration, conversion_rate)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                today,
                random.randint(150, 400),
                random.randint(300, 1200),
                random.uniform(0.3, 0.6),
                random.uniform(120, 480),
                random.uniform(0.02, 0.08)
            )
        )
        
        con.execute(
            """INSERT OR REPLACE INTO business_metrics 
            (date, revenue, new_customers, support_tickets, social_mentions, customer_satisfaction)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                today,
                random.uniform(800, 3000),
                random.randint(2, 8),
                random.randint(1, 5),
                random.randint(3, 15),
                random.uniform(4.0, 5.0)
            )
        )
        
        con.commit()
        print(f"✅ Successfully added data for {today}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    append_today_data()

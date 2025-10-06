import os
import sqlite3
from flask import Flask, render_template, g
from bokeh.embed import components
from bokeh.plotting import figure
from datetime import datetime, timedelta
from business_config import BUSINESS_CONFIG

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "business.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    if db := g.pop("db", None):
        db.close()

@app.route("/")
def business_dashboard():
    db = get_db()
    
    # Get email data without pandas
    email_data = {}
    cursor = db.execute("""
        SELECT date, category, COUNT(*) as count 
        FROM email_analytics 
        WHERE date >= ? 
        GROUP BY date, category
        ORDER BY date
    """, [datetime.utcnow().date() - timedelta(days=30)])
    
    for row in cursor:
        date_str = row['date'] if isinstance(row['date'], str) else row['date'].isoformat()
        if date_str not in email_data:
            email_data[date_str] = {}
        email_data[date_str][row['category']] = row['count']
    
    # Get website traffic data
    traffic_data = []
    cursor = db.execute("""
        SELECT date, visitors, pageviews, conversion_rate 
        FROM website_traffic 
        WHERE date >= ? 
        ORDER BY date
    """, [datetime.utcnow().date() - timedelta(days=30)])
    
    for row in cursor:
        date_str = row['date'] if isinstance(row['date'], str) else row['date'].isoformat()
        traffic_data.append({
            'date': date_str,
            'visitors': row['visitors'],
            'pageviews': row['pageviews'],
            'conversion_rate': row['conversion_rate']
        })
    
    # Get business metrics
    business_data = []
    cursor = db.execute("""
        SELECT date, revenue, new_customers, customer_satisfaction
        FROM business_metrics 
        WHERE date >= ? 
        ORDER BY date
    """, [datetime.utcnow().date() - timedelta(days=30)])
    
    for row in cursor:
        date_str = row['date'] if isinstance(row['date'], str) else row['date'].isoformat()
        business_data.append({
            'date': date_str,
            'revenue': row['revenue'],
            'new_customers': row['new_customers'],
            'customer_satisfaction': row['customer_satisfaction']
        })
    
    charts = create_business_charts(email_data, traffic_data, business_data)
    kpis = calculate_business_kpis(db)
    
    script, div = components(charts)
    
    return render_template("index.html", 
                         script=script, 
                         div=div, 
                         kpi=kpis, 
                         business=BUSINESS_CONFIG,
                         now=datetime.now().strftime("%Y-%m-%d %H:%M"))

def create_business_charts(email_data, traffic_data, business_data):
    charts = []
    
    # Chart 1: Email Volume by Category
    if email_data:
        p1 = figure(height=300, x_axis_type="datetime", title="📧 Daily Email Volume by Category")
        
        # Organize data by category
        categories_data = {}
        for date_str, categories in email_data.items():
            date = datetime.fromisoformat(date_str) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            for category, count in categories.items():
                if category not in categories_data:
                    categories_data[category] = {'dates': [], 'counts': []}
                categories_data[category]['dates'].append(date)
                categories_data[category]['counts'].append(count)
        
        colors = ['#2563eb', '#dc2626', '#16a34a', '#ea580c']
        for i, (category, data) in enumerate(categories_data.items()):
            if data['dates'] and data['counts']:
                p1.line(data['dates'], data['counts'], 
                       line_width=2, color=colors[i % len(colors)],
                       legend_label=category.capitalize())
        
        p1.legend.location = "top_left"
        charts.append(p1)
    
    # Chart 2: Website Traffic
    if traffic_data:
        p2 = figure(height=300, x_axis_type="datetime", title="🌐 Website Traffic")
        
        dates = [datetime.fromisoformat(item['date']) if 'T' in item['date'] else datetime.strptime(item['date'], '%Y-%m-%d') for item in traffic_data]
        visitors = [item['visitors'] for item in traffic_data]
        pageviews = [item['pageviews'] for item in traffic_data]
        
        p2.line(dates, visitors, 
               line_width=2, color='#2563eb', legend_label='Visitors')
        p2.line(dates, [p/5 for p in pageviews], 
               line_width=2, color='#dc2626', legend_label='Pageviews ÷ 5')
        p2.legend.location = "top_left"
        charts.append(p2)
    
    # Chart 3: Business Revenue
    if business_data:
        p3 = figure(height=300, x_axis_type="datetime", title="💰 Revenue & Customers")
        
        dates = [datetime.fromisoformat(item['date']) if 'T' in item['date'] else datetime.strptime(item['date'], '%Y-%m-%d') for item in business_data]
        revenue = [item['revenue'] for item in business_data]
        customers = [item['new_customers'] for item in business_data]
        
        p3.vbar(x=dates, top=revenue,
               width=0.8, color='#2563eb', legend_label='Revenue')
        p3.line(dates, [c * 200 for c in customers],
               line_width=2, color='#dc2626', legend_label='New Customers × 200')
        p3.legend.location = "top_left"
        charts.append(p3)
    
    return charts

def calculate_business_kpis(db):
    today = datetime.utcnow().date()
    
    # Email KPIs
    cursor = db.execute("SELECT COUNT(*) as total_emails FROM email_analytics WHERE date = ?", [today])
    email_row = cursor.fetchone()
    total_emails = email_row['total_emails'] if email_row else 0
    
    # Website KPIs
    cursor = db.execute("SELECT visitors as today_visitors, conversion_rate as today_conversion FROM website_traffic WHERE date = ?", [today])
    web_row = cursor.fetchone()
    today_visitors = web_row['today_visitors'] if web_row else 0
    today_conversion = round((web_row['today_conversion'] if web_row else 0) * 100, 2)
    
    # Business KPIs
    cursor = db.execute("SELECT revenue as today_revenue, new_customers as today_customers FROM business_metrics WHERE date = ?", [today])
    business_row = cursor.fetchone()
    today_revenue = f"R{business_row['today_revenue']:,.2f}" if business_row and business_row['today_revenue'] else "R0.00"
    today_customers = business_row['today_customers'] if business_row else 0
    
    return {
        "total_emails": total_emails,
        "today_visitors": today_visitors,
        "today_conversion": today_conversion,
        "today_revenue": today_revenue,
        "today_customers": today_customers,
        "revenue_growth": "+12.5%",
        "visitor_growth": "+8.3%",
    }

@app.route("/ok")
def ok():
    return "✅ Humbu Store Dashboard is operational!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

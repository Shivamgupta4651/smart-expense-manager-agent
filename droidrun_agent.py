"""
Smart Expense Manager Agent
Droidrun DevSprint 2026 - Round 1 Submission
AI-powered mobile automation for expense tracking
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

# =============================================================================
# DATABASE MODULE
# =============================================================================

class ExpenseDatabase:
    """SQLite database for expense management"""
    
    def __init__(self, db_path='expenses.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                merchant TEXT NOT NULL,
                category TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                source_app TEXT,
                confidence_score REAL DEFAULT 0.0
            )
        ''')
        
        # Budget table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE NOT NULL,
                monthly_limit REAL NOT NULL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                keywords TEXT,
                icon TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.insert_default_categories()
    
    def insert_default_categories(self):
        """Insert default expense categories"""
        categories = {
            'Food & Dining': ['restaurant', 'cafe', 'starbucks', 'zomato', 'swiggy', 'pizza', 'food', 'coffee', 'lunch', 'dinner', 'breakfast'],
            'Transportation': ['uber', 'ola', 'metro', 'bus', 'taxi', 'cab', 'petrol', 'fuel', 'parking', 'train'],
            'Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'broadband', 'recharge'],
            'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'game', 'music', 'entertainment', 'ticket'],
            'Shopping': ['amazon', 'flipkart', 'mall', 'store', 'cloth', 'dress', 'shoe', 'shopping'],
            'Health': ['hospital', 'doctor', 'medicine', 'pharmacy', 'gym', 'fitness', 'health'],
            'Education': ['school', 'college', 'course', 'book', 'tuition', 'coaching', 'exam'],
            'Other': ['misc', 'miscellaneous', 'other']
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for category, keywords in categories.items():
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, keywords)
                    VALUES (?, ?)
                ''', (category, json.dumps(keywords)))
            except:
                pass
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, amount, merchant, category, description='', source_app='', confidence=1.0):
        """Add transaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions 
            (amount, merchant, category, description, source_app, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (amount, merchant, category, description, source_app, confidence))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def set_budget(self, category, monthly_limit):
        """Set budget for category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, monthly_limit)
            VALUES (?, ?)
        ''', (category, monthly_limit))
        
        conn.commit()
        conn.close()
    
    def get_budget(self, category):
        """Get budget for category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT monthly_limit FROM budgets WHERE category = ?', (category,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_transactions(self, days=30, category=None):
        """Get transactions from last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_threshold = datetime.now() - timedelta(days=days)
        
        if category:
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE timestamp > ? AND category = ?
                ORDER BY timestamp DESC
            ''', (date_threshold, category))
        else:
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (date_threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_category_spending(self, days=30):
        """Get spending by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_threshold = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE timestamp > ?
            GROUP BY category
            ORDER BY total DESC
        ''', (date_threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results


# =============================================================================
# EXPENSE PROCESSOR MODULE
# =============================================================================

class ExpenseProcessor:
    """Process and extract expense information"""
    
    def __init__(self, db):
        self.db = db
    
    def extract_from_notification(self, notification_text):
        """Extract expense info from notification text"""
        # Pattern: ₹Amount to/for Merchant
        patterns = [
            r'₹([\d.]+)\s+to\s+(.+?)(?:\s+\||$)',
            r'₹([\d.]+)\s+for\s+(.+?)(?:\s+\||$)',
            r'([\d.]+)\s+INR\s+to\s+(.+?)(?:\s+\||$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, notification_text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                merchant = match.group(2).strip()
                return amount, merchant
        
        return None, None
    
    def detect_payment_app(self, app_name):
        """Detect which payment app"""
        payment_apps = {
            'google_pay': 'Google Pay',
            'phonpe': 'PhonePe',
            'paytm': 'Paytm',
            'whatsapp': 'WhatsApp Pay',
            'gpay': 'Google Pay',
            'upi': 'UPI'
        }
        
        app_lower = app_name.lower()
        for key, value in payment_apps.items():
            if key in app_lower:
                return value
        
        return 'Unknown App'


# =============================================================================
# ML CATEGORIZER MODULE
# =============================================================================

class MLCategorizer:
    """Intelligent expense categorization"""
    
    def __init__(self, db):
        self.db = db
        self.category_keywords = self.load_keywords()
    
    def load_keywords(self):
        """Load category keywords from database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, keywords FROM categories')
        results = cursor.fetchall()
        conn.close()
        
        keywords_dict = {}
        for category, keywords_json in results:
            keywords_dict[category] = json.loads(keywords_json)
        
        return keywords_dict
    
    def categorize(self, merchant, description=''):
        """Categorize expense based on merchant and description"""
        combined_text = f"{merchant} {description}".lower()
        
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    score += 1
                    matches += 1
            
            if matches > 0:
                scores[category] = matches
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 3, 1.0)  # Normalize confidence
            return best_category, confidence
        
        return 'Other', 0.5
    
    def get_category_tips(self, category):
        """Get tips for category spending"""
        tips = {
            'Food & Dining': 'Consider meal prep to reduce food expenses',
            'Transportation': 'Use public transport or carpool to save on fuel',
            'Utilities': 'Monitor utility usage for anomalies',
            'Entertainment': 'Set limits on entertainment spending',
            'Shopping': 'Make a list before shopping to avoid impulse buys',
            'Health': 'Regular checkups can prevent costly emergencies',
            'Education': 'Invest in quality education for better returns',
            'Other': 'Track these expenses for better insights'
        }
        
        return tips.get(category, 'Keep monitoring this category')


# =============================================================================
# AGENT ENGINE MODULE
# =============================================================================

class SmartExpenseAgent:
    """Main Droidrun agent for expense automation"""
    
    def __init__(self):
        self.db = ExpenseDatabase()
        self.processor = ExpenseProcessor(self.db)
        self.categorizer = MLCategorizer(self.db)
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration"""
        config = {
            'auto_categorize': True,
            'daily_summary_time': '21:00',  # 9 PM
            'budget_alert_threshold': 0.80,  # 80%
            'min_confidence': 0.5
        }
        return config
    
    def process_transaction_notification(self, notification_data):
        """
        Process transaction from notification
        Simulates Droidrun capturing payment app notifications
        """
        print(f"\n[AGENT] Processing notification: {notification_data}")
        
        # Extract transaction details
        amount, merchant = self.processor.extract_from_notification(
            notification_data.get('text', '')
        )
        
        if not amount or not merchant:
            print("[AGENT] Could not extract transaction details")
            return False
        
        # Detect payment app
        app_name = self.processor.detect_payment_app(
            notification_data.get('app', '')
        )
        
        # Auto-categorize
        category, confidence = self.categorizer.categorize(merchant)
        
        # Check confidence threshold
        if confidence < self.config['min_confidence']:
            category = 'Other'
        
        # Store in database
        transaction_id = self.db.add_transaction(
            amount=amount,
            merchant=merchant,
            category=category,
            source_app=app_name,
            confidence=confidence
        )
        
        print(f"✅ Transaction recorded:")
        print(f"   Amount: ₹{amount}")
        print(f"   Merchant: {merchant}")
        print(f"   Category: {category} (confidence: {confidence:.0%})")
        print(f"   App: {app_name}")
        
        # Check budget
        self.check_budget_alert(category, amount)
        
        return True
    
    def check_budget_alert(self, category, amount):
        """Check if spending exceeds budget"""
        budget = self.db.get_budget(category)
        
        if not budget:
            return
        
        # Get current month spending
        today = datetime.now()
        month_start = today.replace(day=1)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE category = ? AND timestamp >= ?
        ''', (category, month_start))
        
        result = cursor.fetchone()
        conn.close()
        
        total_spent = result[0] if result[0] else 0
        percentage = total_spent / budget
        
        if percentage >= self.config['budget_alert_threshold']:
            alert_level = "🔴 CRITICAL" if percentage >= 1.0 else "🟡 WARNING"
            print(f"\n{alert_level} Budget Alert:")
            print(f"   Category: {category}")
            print(f"   Spent: ₹{total_spent:.2f} / ₹{budget}")
            print(f"   Usage: {percentage:.0%}")
            
            if percentage >= 1.0:
                print(f"   ❌ Budget EXCEEDED by ₹{total_spent - budget:.2f}")
            else:
                remaining = budget - total_spent
                print(f"   ⚠️  Only ₹{remaining:.2f} remaining")
    
    def generate_daily_summary(self, date=None):
        """Generate daily expense summary"""
        if date is None:
            date = datetime.now().date()
        
        print(f"\n{'='*60}")
        print(f"📊 DAILY EXPENSE SUMMARY - {date.strftime('%A, %B %d, %Y')}")
        print(f"{'='*60}")
        
        # Get today's transactions
        transactions = self.db.get_transactions(days=1)
        
        if not transactions:
            print("No transactions today")
            return
        
        total_spent = 0
        category_breakdown = defaultdict(float)
        transaction_count = 0
        
        for trans in transactions:
            # trans: id, amount, merchant, category, timestamp, description, source_app, confidence
            amount = trans[1]
            category = trans[3]
            merchant = trans[2]
            
            total_spent += amount
            category_breakdown[category] += amount
            transaction_count += 1
        
        # Print summary
        print(f"\n💰 Total Spent: ₹{total_spent:.2f}")
        print(f"📍 Transactions: {transaction_count}")
        
        print(f"\n📈 Breakdown by Category:")
        for category, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            bar_length = int(percentage / 5)
            bar = "█" * bar_length
            print(f"   {category:20} ₹{amount:8.2f} ({percentage:5.1f}%) {bar}")
        
        # Calculate vs average
        prev_transactions = self.db.get_transactions(days=30)
        if len(prev_transactions) > 1:
            prev_total = sum(t[1] for t in prev_transactions)
            avg_daily = prev_total / 30
            diff = total_spent - avg_daily
            diff_percent = (diff / avg_daily * 100) if avg_daily > 0 else 0
            
            print(f"\n📉 Comparison:")
            print(f"   30-day Average: ₹{avg_daily:.2f}/day")
            if diff > 0:
                print(f"   Today: {diff_percent:+.1f}% above average")
            else:
                print(f"   Today: {abs(diff_percent):.1f}% below average")
        
        # Insights
        print(f"\n💡 Insights:")
        top_category = max(category_breakdown.items(), key=lambda x: x[1])
        print(f"   • Highest spending: {top_category[0]} (₹{top_category[1]:.2f})")
        
        tip = self.categorizer.get_category_tips(top_category[0])
        print(f"   • Tip: {tip}")
        
        print(f"\n{'='*60}\n")
    
    def generate_monthly_report(self):
        """Generate monthly expense report"""
        print(f"\n{'='*60}")
        print(f"📅 MONTHLY EXPENSE REPORT")
        print(f"{'='*60}")
        
        transactions = self.db.get_transactions(days=30)
        
        if not transactions:
            print("No transactions this month")
            return
        
        # Category analysis
        category_data = self.db.get_category_spending(days=30)
        total_spent = sum(cat[1] for cat in category_data)
        
        print(f"\n💰 Total Monthly Spending: ₹{total_spent:.2f}")
        print(f"\n📊 Category Breakdown:")
        
        for category, amount, count in category_data:
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            avg_per_transaction = amount / count if count > 0 else 0
            
            print(f"   {category:20} ₹{amount:10.2f} ({percentage:5.1f}%) - {count} transactions (avg: ₹{avg_per_transaction:.2f})")
        
        # Budget status
        print(f"\n📌 Budget Status:")
        for category, amount, _ in category_data:
            budget = self.db.get_budget(category)
            if budget:
                percentage = (amount / budget * 100)
                status = "✅" if percentage <= 100 else "❌"
                print(f"   {status} {category:20} {percentage:6.1f}% (₹{amount:.2f}/₹{budget:.2f})")
        
        print(f"\n{'='*60}\n")
    
    def setup_demo_budgets(self):
        """Setup demo budgets"""
        demo_budgets = {
            'Food & Dining': 3000,
            'Transportation': 2000,
            'Entertainment': 1500,
            'Shopping': 2500,
            'Utilities': 2000,
            'Health': 1000
        }
        
        for category, limit in demo_budgets.items():
            self.db.set_budget(category, limit)
        
        print("✅ Demo budgets created")
    
    def run_demo(self):
        """Run demonstration with sample data"""
        print("\n" + "="*60)
        print("🤖 SMART EXPENSE MANAGER AGENT - DEMO")
        print("="*60)
        
        # Setup
        self.setup_demo_budgets()
        
        # Demo transactions
        demo_transactions = [
            {'text': '₹250 to Starbucks Coffee', 'app': 'Google Pay'},
            {'text': '₹450 for Uber ride', 'app': 'GPay'},
            {'text': '₹1200 to Amazon Purchase', 'app': 'PhonePe'},
            {'text': '₹500 for Netflix Subscription', 'app': 'Google Pay'},
            {'text': '₹3000 to Apollo Hospital', 'app': 'UPI'},
            {'text': '₹800 to Zomato Food Delivery', 'app': 'PhonePe'},
        ]
        
        print("\n[DEMO] Processing sample transactions...")
        for i, transaction in enumerate(demo_transactions, 1):
            print(f"\n--- Transaction {i} ---")
            self.process_transaction_notification(transaction)
        
        # Generate summaries
        self.generate_daily_summary()
        self.generate_monthly_report()
        
        print("\n✅ Demo completed successfully!")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    # Initialize and run agent
    agent = SmartExpenseAgent()
    agent.run_demo()

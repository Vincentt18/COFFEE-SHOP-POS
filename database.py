import sqlite3
import datetime
import json

class DatabaseManager:
    def __init__(self, db_path='coffee_pos.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._init_db()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def _init_db(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS menu
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL
                                UNIQUE,
                                price
                                REAL
                                NOT
                                NULL,
                                stock
                                INTEGER
                                NOT
                                NULL,
                                category
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS sales
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                item_name
                                TEXT
                                NOT
                                NULL,
                                category
                                TEXT
                                NOT
                                NULL,
                                quantity
                                INTEGER
                                NOT
                                NULL,
                                price
                                REAL
                                NOT
                                NULL,
                                total
                                REAL
                                NOT
                                NULL,
                                sale_date
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS eod_summary
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                report_date
                                TEXT
                                NOT
                                NULL
                                UNIQUE,
                                total_revenue
                                REAL
                                NOT
                                NULL,
                                top_items_json
                                TEXT,
                                low_stock_json
                                TEXT
                            )
                            """)
        
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS eod_summary_archive
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                report_date TEXT NOT NULL UNIQUE,
                                total_revenue REAL NOT NULL,
                                top_items_json TEXT,
                                low_stock_json TEXT,
                                archived_at TEXT NOT NULL
                            )
                            """)
        
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL UNIQUE,
                                password TEXT NOT NULL,
                                role TEXT NOT NULL,
                                created_at TEXT NOT NULL
                            )
                            """)
        
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS receipts
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                receipt_uuid TEXT NOT NULL UNIQUE,
                                sale_date TEXT NOT NULL,
                                total REAL NOT NULL,
                                items_json TEXT NOT NULL,
                                created_at TEXT NOT NULL
                            )
                            """)
        self.conn.commit()
        self._seed_data()

    def _seed_data(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM menu")
            if self.cursor.fetchone()[0] == 0:
                initial_items = [
                   
                    ('Espresso', 90.00, 100, 'Coffee'),
                    ('Latte', 80.00, 150, 'Coffee'),
                    ('Cappuccino', 100.00, 120, 'Coffee'),
                    ('Mocha', 110.00, 90, 'Coffee'),
                    ('Americano', 75.00, 130, 'Coffee'),
                    ('Flat White', 105.00, 80, 'Coffee'),
                    ('Macchiato', 95.00, 110, 'Coffee'),
                    ('Affogato', 120.00, 70, 'Coffee'),
                    ('Pour Over', 130.00, 60, 'Coffee'),

                   
                    ('Croissant', 70.00, 50, 'Pastry'),
                    ('Blueberry Muffin', 70.00, 60, 'Pastry'),
                    ('Chocolate Chip Cookie', 50.00, 90, 'Pastry'),
                    ('Cinnamon Roll', 85.00, 45, 'Pastry'),
                    ('Cheese Danish', 95.00, 35, 'Pastry'),
                    ('Lemon Bar', 65.00, 55, 'Pastry'),
                    ('Red Velvet Cake Slice', 150.00, 30, 'Pastry'),
                    ('Apple Turnover', 75.00, 40, 'Pastry'),
                    ('Almond Biscotti', 40.00, 75, 'Pastry'),

                    
                    ('Iced Tea', 60.00, 80, 'Beverage'),
                    ('Orange Juice', 70.00, 70, 'Beverage'),
                    ('Lemonade', 75.00, 90, 'Beverage'),
                    ('Sparkling Water', 50.00, 100, 'Beverage'),
                    ('Hot Chocolate', 110.00, 60, 'Beverage'),
                    ('Green Tea', 55.00, 85, 'Beverage'),
                    ('Mango Smoothie', 140.00, 40, 'Beverage'),
                    ('Strawberry Milkshake', 160.00, 30, 'Beverage'),
                    ('Caramel Frappe', 155.00, 50, 'Beverage'),


                    ('Tuna Sandwich', 50.00, 30, 'Food'),
                    ('Chicken Pesto Sandwich', 180.00, 25, 'Food'),
                    ('Caesar Salad', 190.00, 20, 'Food'),
                    ('Beef Lasagna', 250.00, 15, 'Food'),
                    ('Breakfast Burrito', 160.00, 35, 'Food'),
                    ('Vegetarian Wrap', 150.00, 40, 'Food'),
                    ('Pasta Carbonara', 220.00, 18, 'Food'),
                    ('Waffles and Syrup', 130.00, 22, 'Food'),
                    ('Fries', 90.00, 50, 'Food'),
                ]
                self.cursor.executemany("INSERT INTO menu (name, price, stock, category) VALUES (?, ?, ?, ?)",
                                        initial_items)
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error seeding data: {e}")

        try:
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()[0] == 0:
                default_users = [
                    ('manager', 'admin123', 'Manager'),
                    ('cashier', 'password', 'Cashier')
                ]
                for u, p, r in default_users:
                    try:
                        self.cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, datetime('now'))", (u, p, r))
                    except sqlite3.IntegrityError:
                        pass
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error seeding users: {e}")
        except sqlite3.Error as e:
            print(f"Error seeding data: {e}")

    def create_menu_item(self, name, price, stock, category):
        try:
            self.cursor.execute("INSERT INTO menu (name, price, stock, category) VALUES (?, ?, ?, ?)",
                                (name, price, stock, category))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def read_menu_items(self):
        self.cursor.execute("SELECT id, name, price, stock, category FROM menu ORDER BY name ASC")
        return self.cursor.fetchall()

    def read_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM menu ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def update_menu_item(self, item_id, name, price, stock, category):
        try:
            self.cursor.execute("UPDATE menu SET name=?, price=?, stock=?, category=? WHERE id=?",
                                (name, price, stock, category, item_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_menu_item(self, item_id):
        try:
            self.cursor.execute("DELETE FROM menu WHERE id=?", (item_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def get_item_details(self, item_id):
        self.cursor.execute("SELECT name, price, category FROM menu WHERE id = ?", (item_id,))
        return self.cursor.fetchone()
    
    def create_user(self, username, password, role='Cashier'):
        try:
            self.cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, datetime('now'))", (username, password, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def get_user(self, username):
        try:
            self.cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            if row:
                return {'username': row[0], 'password': row[1], 'role': row[2]}
            return None
        except sqlite3.Error:
            return None

    def list_users(self):
        try:
            self.cursor.execute("SELECT username, role FROM users ORDER BY username")
            return [{'username': r[0], 'role': r[1]} for r in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def update_user_password(self, username, new_password):
        try:
            self.cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_user(self, username):
        try:
            self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def record_sale(self, order_items, sale_date):
        try:
            for item in order_items:
                name = item['name']
                qty = item['qty']
                price = item['price']
                category = item['category']
                total = price * qty

                self.cursor.execute(
                    "INSERT INTO sales (item_name, category, quantity, price, total, sale_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, category, qty, price, total, sale_date)
                )
                self.cursor.execute("UPDATE menu SET stock = stock - ? WHERE name = ?", (qty, name))
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def save_receipt(self, receipt_uuid, sale_date, total, items):
        """Save a receipt record. `items` should be JSON-serializable (list/dict). Returns inserted id or None."""
        try:
            items_json = json.dumps(items)
            self.cursor.execute(
                "INSERT INTO receipts (receipt_uuid, sale_date, total, items_json, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (receipt_uuid, sale_date, total, items_json)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        except sqlite3.Error:
            return None

    def get_receipt(self, receipt_uuid):
        try:
            self.cursor.execute("SELECT receipt_uuid, sale_date, total, items_json, created_at FROM receipts WHERE receipt_uuid = ?", (receipt_uuid,))
            row = self.cursor.fetchone()
            if not row:
                return None
            return {
                'receipt_uuid': row[0],
                'sale_date': row[1],
                'total': row[2],
                'items': json.loads(row[3]),
                'created_at': row[4]
            }
        except sqlite3.Error:
            return None

    def delete_receipt(self, receipt_uuid):
        """Delete a receipt by UUID. Returns True if successful, False otherwise."""
        try:
            self.cursor.execute("DELETE FROM receipts WHERE receipt_uuid = ?", (receipt_uuid,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def get_sales_data_for_report(self, days_back=30):
        date_limit = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            f"SELECT item_name, category, quantity, total, strftime('%Y-%m-%d', sale_date) FROM sales WHERE sale_date >= ?",
            (date_limit,))
        return self.cursor.fetchall()

    def end_of_day_summary(self, target_date_str):
        self.cursor.execute(
            "SELECT SUM(total) FROM sales WHERE strftime('%Y-%m-%d', sale_date) = ?", (target_date_str,))
        total_revenue = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("""
                            SELECT item_name, SUM(quantity) as total_qty
                            FROM sales
                            WHERE strftime('%Y-%m-%d', sale_date) = ?
                            GROUP BY item_name
                            ORDER BY total_qty DESC LIMIT 3
                            """, (target_date_str,))
        top_items = self.cursor.fetchall()

        self.cursor.execute("""
                            SELECT name, stock
                            FROM menu
                            WHERE stock < 10
                            ORDER BY stock ASC
                            """)
        low_stock = self.cursor.fetchall()

        return {
            'date': target_date_str,
            'total_revenue': total_revenue,
            'top_items': top_items,
            'low_stock': low_stock
        }

    def save_eod_summary(self, summary_data):
        try:
            top_items_json = json.dumps(summary_data['top_items'])
            low_stock_json = json.dumps(summary_data['low_stock'])
            self.cursor.execute(
                "INSERT INTO eod_summary (report_date, total_revenue, top_items_json, low_stock_json) VALUES (?, ?, ?, ?)",
                (summary_data['date'], summary_data['total_revenue'], top_items_json, low_stock_json)
            )
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO eod_summary_archive (report_date, total_revenue, top_items_json, low_stock_json, archived_at) VALUES (?, ?, ?, ?, datetime('now'))",
                    (summary_data['date'], summary_data['total_revenue'], top_items_json, low_stock_json)
                )
            except Exception:
                pass
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error saving EOD summary: {e}")
            return False

    def get_past_eod_records(self):
        self.cursor.execute(
            "SELECT report_date, total_revenue, top_items_json, low_stock_json FROM eod_summary ORDER BY report_date DESC"
        )
        records = self.cursor.fetchall()
        parsed_records = []
        for date, revenue, top_json, low_json in records:
            parsed_records.append({
                'date': date,
                'revenue': revenue,
                'top_items': json.loads(top_json),
                'low_stock': json.loads(low_json)
            })
        return parsed_records

    def clear_all_sales_data(self):
        try:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO eod_summary_archive (report_date, total_revenue, top_items_json, low_stock_json, archived_at) SELECT report_date, total_revenue, top_items_json, low_stock_json, datetime('now') FROM eod_summary"
                )
            except Exception:
                pass

            self.cursor.execute("DELETE FROM sales")
            self.cursor.execute("DELETE FROM eod_summary")
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_archived_eod_records(self):
        self.cursor.execute(
            "SELECT report_date, total_revenue, top_items_json, low_stock_json, archived_at FROM eod_summary_archive ORDER BY archived_at DESC"
        )
        records = self.cursor.fetchall()
        parsed = []
        for date, revenue, top_json, low_json, archived_at in records:
            parsed.append({
                'date': date,
                'revenue': revenue,
                'top_items': json.loads(top_json),
                'low_stock': json.loads(low_json),
                'archived_at': archived_at
            })
        return parsed

    def restore_all_archived_eod_records(self):
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO eod_summary (report_date, total_revenue, top_items_json, low_stock_json) SELECT report_date, total_revenue, top_items_json, low_stock_json FROM eod_summary_archive"
            )
            self.conn.commit()
            self.cursor.execute("SELECT COUNT(*) FROM eod_summary")
            return self.cursor.fetchone()[0]
        except sqlite3.Error:
            return 0

    def get_all_receipts(self, limit=None):
        try:
            query = "SELECT receipt_uuid, sale_date, total, items_json, created_at FROM receipts ORDER BY created_at DESC"
            if limit and isinstance(limit, int):
                query = query + f" LIMIT {limit}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            results = []
            for receipt_uuid, sale_date, total, items_json, created_at in rows:
                try:
                    items = json.loads(items_json)
                except Exception:
                    items = []
                results.append({
                    'receipt_uuid': receipt_uuid,
                    'sale_date': sale_date,
                    'total': total,
                    'items': items,
                    'created_at': created_at
                })
            return results
        except sqlite3.Error:
            return []
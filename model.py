import datetime
from database import DatabaseManager


class AppModel:
    def __init__(self):
        self.db = DatabaseManager()
        self.credentials = {}
        self.user_role = None
        self.current_pos_date = datetime.date.today()
        self.current_order = {}

    def authenticate(self, username, password):
        username = username.lower().strip()
        password = password.strip()
        user = self.db.get_user(username)
        if user and user.get('password') == password:
            self.user_role = user.get('role')
            return True
        self.user_role = None
        return False

    def update_password(self, username, old_password, new_password):
        username = username.lower().strip()
        user = self.db.get_user(username)
        if not user:
            return "User not found"

        if user.get('password') != old_password:
            return "Incorrect old password"

        if old_password == new_password:
            return "New password cannot be the same as old password"

        ok = self.db.update_user_password(username, new_password)
        return "Success" if ok else "Failed to update password"

    def get_usernames(self):
        users = self.db.list_users()
        return [u['username'] for u in users]

    def create_user(self, username, password, role='Cashier'):
        return self.db.create_user(username, password, role)

    def delete_user(self, username):
        return self.db.delete_user(username)

    def add_item_to_order(self, item_id):
        item_details = self.db.get_item_details(item_id)
        if not item_details:
            return False, "Item not found in menu."

        name, price, category = item_details

        if item_id in self.current_order:
            self.current_order[item_id]['qty'] += 1
        else:
            self.current_order[item_id] = {'name': name, 'price': price, 'qty': 1, 'category': category}

        return True, "Item added"

    def calculate_order_total(self):
        total = sum(item['price'] * item['qty'] for item in self.current_order.values())
        return total

    def process_order(self):
        if not self.current_order:
            return False, 0, None

        order_list = list(self.current_order.values())
        sale_date = self.current_pos_date.strftime('%Y-%m-%d') + datetime.datetime.now().strftime(' %H:%M:%S')

        success = self.db.record_sale(order_list, sale_date)

        if success:
            total = self.calculate_order_total()
            # create a receipt UUID and persist receipt details in DB
            try:
                import uuid
                receipt_uuid = uuid.uuid4().hex
                saved_id = self.db.save_receipt(receipt_uuid, sale_date, total, order_list)
                receipt_ref = receipt_uuid if saved_id else None
            except Exception:
                receipt_ref = None

            self.current_order = {}
            return True, total, receipt_ref

        return False, 0, None

    def remove_item_from_order(self, item_id):
        if item_id in self.current_order:
            del self.current_order[item_id]
            return True
        return False

    def clear_order(self):
        self.current_order = {}

    def get_menu_items(self):
        return self.db.read_menu_items()

    def get_menu_categories(self):
        return self.db.read_categories()

    def get_all_sales_data(self, days_back=30):
        return self.db.get_sales_data_for_report(days_back)

    def generate_eod_summary(self):
        current_date_str = self.current_pos_date.strftime('%Y-%m-%d')
        return self.db.end_of_day_summary(current_date_str)

    def save_eod_and_advance_day(self):
        summary = self.generate_eod_summary()

        if not self.db.save_eod_summary(summary):
            return "Already Saved", summary

        self.current_pos_date += datetime.timedelta(days=1)
        return "Success", summary

    def get_historical_eod_records(self):
        return self.db.get_past_eod_records()

    def get_all_receipts(self, limit=None):
        try:
            return self.db.get_all_receipts(limit=limit)
        except Exception:
            return []

    def delete_receipt(self, receipt_uuid):
        """Delete a receipt from the database by its UUID."""
        try:
            return self.db.delete_receipt(receipt_uuid)
        except Exception:
            return False

    def get_archived_eod_records(self):
        return self.db.get_archived_eod_records()

    def restore_archived_eod_summaries(self):
        try:
            return self.db.restore_all_archived_eod_records()
        except Exception:
            return None

    def create_item(self, name, price, stock, category):
        return self.db.create_menu_item(name, price, stock, category)

    def update_item(self, item_id, name, price, stock, category):
        return self.db.update_menu_item(item_id, name, price, stock, category)

    def delete_item(self, item_id):
        return self.db.delete_menu_item(item_id)

    def clear_historical_data(self):
        return self.db.clear_all_sales_data()
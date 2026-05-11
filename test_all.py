import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import datetime

class TestAppModel(unittest.TestCase):
    def setUp(self):
        with patch('model.DatabaseManager'):
            from model import AppModel
            self.model = AppModel()
            self.model.db = Mock()
    
    def test_model_init(self):
        """Test model initialization"""
        self.assertIsNotNone(self.model.db)
        self.assertIsNone(self.model.user_role)
        self.assertEqual(self.model.current_order, {})
        self.assertIsInstance(self.model.current_pos_date, datetime.date)
    
    def test_authenticate_success(self):
        """Test successful authentication"""
        self.model.db.get_user.return_value = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'Cashier'
        }
        
        result = self.model.authenticate('testuser', 'testpass')
        
        self.assertTrue(result)
        self.assertEqual(self.model.user_role, 'Cashier')
    
    def test_authenticate_failure_invalid_password(self):
        """Test authentication with invalid password"""
        self.model.db.get_user.return_value = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'Cashier'
        }
        
        result = self.model.authenticate('testuser', 'wrongpass')
        
        self.assertFalse(result)
        self.assertIsNone(self.model.user_role)
    
    def test_authenticate_failure_user_not_found(self):
        """Test authentication with non-existent user"""
        self.model.db.get_user.return_value = None
        
        result = self.model.authenticate('nonexistent', 'password')
        
        self.assertFalse(result)
        self.assertIsNone(self.model.user_role)
    
    def test_authenticate_username_normalization(self):
        """Test that username is normalized (lowercased and stripped)"""
        self.model.db.get_user.return_value = {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'Manager'
        }
        
        self.model.authenticate('  TestUser  ', 'testpass')
        
        self.model.db.get_user.assert_called_with('testuser')
    
    def test_add_item_to_order_success(self):
        self.model.db.get_item_details.return_value = ('Coffee', 5.99, 'Beverages')
        
        success, message = self.model.add_item_to_order(1)
        
        self.assertTrue(success)
        self.assertEqual(message, "Item added")
        self.assertIn(1, self.model.current_order)
        self.assertEqual(self.model.current_order[1]['name'], 'Coffee')
        self.assertEqual(self.model.current_order[1]['qty'], 1)
    
    def test_add_item_to_order_increase_quantity(self):
        self.model.db.get_item_details.return_value = ('Coffee', 5.99, 'Beverages')
        
        self.model.add_item_to_order(1)
        self.model.add_item_to_order(1)
        
        self.assertEqual(self.model.current_order[1]['qty'], 2)
    
    def test_add_item_to_order_item_not_found(self):
        self.model.db.get_item_details.return_value = None
        
        success, message = self.model.add_item_to_order(999)
        
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_calculate_order_total(self):
        self.model.current_order = {
            1: {'name': 'Coffee', 'price': 5.99, 'qty': 2, 'category': 'Beverages'},
            2: {'name': 'Pastry', 'price': 3.50, 'qty': 1, 'category': 'Food'}
        }
        
        total = self.model.calculate_order_total()
        
        expected_total = (5.99 * 2) + (3.50 * 1)
        self.assertAlmostEqual(total, expected_total, places=2)
    
    def test_calculate_order_total_empty_order(self):
        self.model.current_order = {}
        
        total = self.model.calculate_order_total()
        
        self.assertEqual(total, 0)
    
    def test_remove_item_from_order_success(self):
        self.model.current_order = {1: {'name': 'Coffee', 'qty': 1}}
        
        result = self.model.remove_item_from_order(1)
        
        self.assertTrue(result)
        self.assertNotIn(1, self.model.current_order)
    
    def test_remove_item_from_order_not_found(self):
        self.model.current_order = {}
        
        result = self.model.remove_item_from_order(1)
        
        self.assertFalse(result)
    
    def test_clear_order(self):
        self.model.current_order = {1: {'name': 'Coffee', 'qty': 1}}
        
        self.model.clear_order()
        
        self.assertEqual(self.model.current_order, {})
    
    def test_update_password_success(self):
        self.model.db.get_user.return_value = {
            'username': 'testuser',
            'password': 'oldpass'
        }
        self.model.db.update_user_password.return_value = True
        
        result = self.model.update_password('testuser', 'oldpass', 'newpass')
        
        self.assertEqual(result, "Success")
        self.model.db.update_user_password.assert_called_with('testuser', 'newpass')
    
    def test_update_password_wrong_old_password(self):
        self.model.db.get_user.return_value = {
            'username': 'testuser',
            'password': 'oldpass'
        }
        
        result = self.model.update_password('testuser', 'wrongpass', 'newpass')
        
        self.assertEqual(result, "Incorrect old password")
    
    def test_get_usernames(self):
        self.model.db.list_users.return_value = [
            {'username': 'user1'},
            {'username': 'user2'},
            {'username': 'user3'}
        ]
        
        usernames = self.model.get_usernames()
        
        self.assertEqual(usernames, ['user1', 'user2', 'user3'])

# DATABASE TESTS
class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        from database import DatabaseManager
        self.db_manager = DatabaseManager(':memory:')
    
    def tearDown(self):
        if self.db_manager.conn:
            self.db_manager.conn.close()
    
    def test_database_init(self):
        self.assertIsNotNone(self.db_manager.conn)
        self.assertIsNotNone(self.db_manager.cursor)
        self.assertEqual(self.db_manager.db_path, ':memory:')
    
    def test_init_creates_tables(self):
        cursor = self.db_manager.cursor
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        self.assertIsNotNone(cursor.fetchone())
    
    def test_create_user(self):
        result = self.db_manager.create_user('testuser', 'password123', 'Cashier')
        
        self.assertTrue(result)
    
    def test_get_user(self):
        self.db_manager.create_user('testuser', 'password123', 'Cashier')
        
        user = self.db_manager.get_user('testuser')
        
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['password'], 'password123')
        self.assertEqual(user['role'], 'Cashier')
    
    def test_list_users(self):
        self.db_manager.create_user('user1', 'pass1', 'Cashier')
        self.db_manager.create_user('user2', 'pass2', 'Manager')
        
        users = self.db_manager.list_users()
        
        self.assertGreaterEqual(len(users), 2)
    
    def test_update_user_password(self):
        self.db_manager.create_user('testuser', 'oldpass', 'Cashier')
        
        result = self.db_manager.update_user_password('testuser', 'newpass')
        
        self.assertTrue(result)
        
        user = self.db_manager.get_user('testuser')
        self.assertEqual(user['password'], 'newpass')
    
    def test_delete_user(self):
        self.db_manager.create_user('testuser', 'password', 'Cashier')
        
        result = self.db_manager.delete_user('testuser')
        
        self.assertTrue(result)
        
        user = self.db_manager.get_user('testuser')
        self.assertIsNone(user)
    
    def test_save_receipt(self):
        order_list = [{'name': 'Espresso', 'price': 3.50, 'qty': 1}]
        
        receipt_id = self.db_manager.save_receipt(
            'receipt123',
            '2025-01-01 10:00:00',
            3.50,
            order_list
        )
        
        self.assertIsNotNone(receipt_id)

# CONTROLLER TESTS
class TestAppController(unittest.TestCase):
    
    def setUp(self):
        self.mock_model = Mock()
        self.mock_app = Mock()
        
        with patch('controller.LoginDialog'):
            with patch('controller.CoffeeShopPOSView'):
                from controller import AppController
                self.controller = AppController(self.mock_model, self.mock_app)
    
    def test_controller_init(self):
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertEqual(self.controller.app, self.mock_app)
        self.assertIsNotNone(self.controller.model)
    
    @patch('controller.LoginDialog')
    def test_init_login_flow_first_time(self, mock_login_dialog_class):
        mock_dialog_instance = Mock()
        mock_login_dialog_class.return_value = mock_dialog_instance
        mock_dialog_instance.exec_.return_value = 1
        
        with patch('controller.CoffeeShopPOSView'):
            from controller import AppController
            controller = AppController(self.mock_model, self.mock_app)
        
        mock_login_dialog_class.assert_called()
        mock_dialog_instance.exec_.assert_called()
    
    def test_handle_logout(self):
        self.controller.main_window = Mock()
        self.controller.main_window.show_info = Mock()
        
        with patch.object(self.controller, 'init_login_flow'):
            self.controller.handle_logout()
            self.controller.init_login_flow.assert_called()
    
    def test_refresh_all_data_cashier(self):
        self.mock_model.user_role = 'Cashier'
        self.mock_model.get_menu_items.return_value = []
        self.mock_model.current_order = {}
        self.mock_model.calculate_order_total.return_value = 0
        
        self.controller.main_window = Mock()
        
        self.controller.refresh_all_data()
        
        self.mock_model.get_menu_items.assert_called()
        self.controller.main_window.update_menu_display.assert_called()
    
    def test_refresh_all_data_manager(self):
        self.mock_model.user_role = 'Manager'
        self.mock_model.get_menu_items.return_value = []
        self.mock_model.current_order = {}
        self.mock_model.calculate_order_total.return_value = 0
        self.mock_model.get_menu_categories.return_value = ['Coffee', 'Pastry']
        self.mock_model.get_usernames.return_value = ['user1', 'user2']
        
        self.controller.main_window = Mock()
        
        self.controller.refresh_all_data()
        
        self.mock_model.get_menu_items.assert_called()
        self.controller.main_window.update_admin_menu_table.assert_called()



# VIEW TESTS
class TestViewComponents(unittest.TestCase):
    
    def test_view_imports(self):
        try:
            import view
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import view module: {e}")
    
    def test_create_label(self):
        from view import create_label
        
        with patch('view.QLabel') as mock_label:
            label = create_label("Test Label", font_size=12, bold=False)
            self.assertIsNotNone(label)
    
    def test_create_button_primary(self):
        from view import create_button
        
        with patch('view.QPushButton'):
            button = create_button("Test Button", style_class="primary")
            self.assertIsNotNone(button)
    
    def test_create_button_secondary(self):
        from view import create_button
        
        with patch('view.QPushButton'):
            button = create_button("Test Button", style_class="secondary")
            self.assertIsNotNone(button)

# MAIN TESTS
class TestMainModule(unittest.TestCase):
    
    @patch('main.QApplication')
    @patch('main.AppController')
    @patch('main.AppModel')
    @patch('main.sys.exit')
    def test_main_imports(self, mock_exit, mock_model, mock_controller, mock_app):
        try:
            import main
            self.assertIsNotNone(main.QApplication)
            self.assertIsNotNone(main.AppModel)
            self.assertIsNotNone(main.AppController)
        except ImportError as e:
            self.fail(f"Failed to import required modules in main: {e}")
    
    def test_main_is_executable(self):
        main_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        with open(main_file, 'r') as f:
            content = f.read()
            self.assertIn("if __name__ == '__main__'", content)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestAppModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAppController))
    suite.addTests(loader.loadTestsFromTestCase(TestViewComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestMainModule))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)

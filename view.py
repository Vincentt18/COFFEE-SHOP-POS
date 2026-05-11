import pandas as pd
import json
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QGridLayout, QHeaderView,
    QComboBox, QSizePolicy, QGroupBox, QDialog, QStackedWidget) # Added QStackedWidget
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

if 'qt5' not in plt.get_backend().lower():
    try:
        plt.switch_backend('Qt5Agg')
    except ImportError:
        pass

class GraphCanvas(FigureCanvas):
    def __init__(self, title, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax.set_title(title, fontsize=12, color='#6F4E37')
        self.fig.tight_layout()
        self.updateGeometry()

    def clear_plot(self, title):
        self.ax.clear()
        self.ax.set_title(title, fontsize=12, color='#6F4E37')
        self.ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.draw()

    def plot_top_selling_items(self, df):
        title = "Top 5 Selling Items (Quantity)"
        if df.empty: return self.clear_plot(title)
        self.ax.clear()
        self.ax.set_title(title, fontsize=14, color='#6F4E37')
        item_qty = df.groupby('item_name')['quantity'].sum().nlargest(5)
        self.ax.bar(item_qty.index, item_qty.values, color='#A0522D')
        self.ax.set_ylabel('Total Quantity Sold', fontsize=10)
        self.ax.tick_params(axis='x', rotation=45, labelsize=8)
        self.fig.tight_layout()
        self.draw()

    def plot_sales_by_category(self, df):
        title = "Revenue Share by Category"
        if df.empty: return self.clear_plot(title)
        self.ax.clear()
        self.ax.set_title(title, fontsize=14, color='#6F4E37')
        category_revenue = df.groupby('category')['total'].sum()
        labels = category_revenue.index
        values = category_revenue.values
        colors = ['#6F4E37', '#8B4513', '#A0522D', '#CD853F', '#DEB887', '#D2B48C']
        self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)])
        self.ax.axis('equal')
        self.fig.tight_layout()
        self.draw()

    def plot_daily_sales(self, df):
        title = "Daily Revenue Trend"
        if df.empty: return self.clear_plot(title)
        self.ax.clear()
        self.ax.set_title(title, fontsize=14, color='#6F4E37')
        daily_revenue = df.groupby('date')['total'].sum().reset_index()
        daily_revenue['date'] = pd.to_datetime(daily_revenue['date'])
        daily_revenue = daily_revenue.sort_values(by='date')
        labels = daily_revenue['date'].dt.strftime('%m-%d').tolist()
        values = daily_revenue['total'].tolist()
        self.ax.plot(labels, values, marker='o', color='#8B4513', linewidth=2)
        self.ax.set_ylabel('Revenue (₱)', fontsize=10)
        self.ax.set_xlabel('Date', fontsize=10)
        self.ax.tick_params(axis='x', rotation=45, labelsize=8)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.fig.tight_layout()
        self.draw()


def create_label(text, font_size=12, bold=False):
    label = QLabel(text)
    font = QFont("Inter", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setStyleSheet("color: #6F4E37;")
    return label

def create_button(text, style_class="primary"):
    button = QPushButton(text)
    button.setFont(QFont("Inter", 11, QFont.Bold))
    if style_class == "primary":
        style = """
            QPushButton {background-color: #A0522D; color: white; border: 1px solid #8B4513; border-radius: 8px; padding: 10px 20px;}
            QPushButton:hover {background-color: #CD853F;}
        """
    elif style_class == "secondary":
        style = """
            QPushButton {background-color: #D2B48C; color: #6F4E37; border: 1px solid #6F4E37; border-radius: 8px; padding: 10px 15px;}
            QPushButton:hover {background-color: #DEB887;}
        """
    elif style_class == "danger":
        style = """
            QPushButton {background-color: #CC0000; color: white; padding: 10px 15px; border-radius: 8px;}
            QPushButton:hover {background-color: #FF3333;}
        """
    button.setStyleSheet(style)
    return button


def create_input(placeholder, is_password=False):
    line_edit = QLineEdit()
    line_edit.setPlaceholderText(placeholder)
    line_edit.setFont(QFont("Inter", 10))
    if is_password:
        line_edit.setEchoMode(QLineEdit.Password)
    line_edit.setStyleSheet("""
        QLineEdit {padding: 8px; border: 1px solid #D2B48C; border-radius: 5px; background-color: white; color: #4A2C2A;}
    """)
    return line_edit

class LoginDialog(QDialog):
    login_attempted = pyqtSignal(str, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS System Login")
        self.setFixedSize(600, 450)
        self._setup_style()
        self._setup_ui()

    def _setup_style(self):
        self.setStyleSheet("""
            QDialog {background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #6F4E37, stop: 1 #4A2C2A); border: 2px solid #D2B48C;}
            QLabel#titleLabel {color: #4A2C2A; font-size: 24pt; font-weight: bold;}
            QWidget#loginFormContainer {background-color: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 30px; min-width: 300px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);}
        """)

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        form_container = QWidget()
        form_container.setObjectName("loginFormContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setAlignment(Qt.AlignCenter)

        title_label = create_label("Welcome to CoffeePOS", 18, True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        form_layout.addWidget(title_label)

        subtitle_label = create_label("Sign in to continue", 12, False)
        subtitle_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(subtitle_label)

        self.username_input = create_input("Username (manager/cashier)")
        form_layout.addWidget(self.username_input)

        self.password_input = create_input("Password", is_password=True)
        form_layout.addWidget(self.password_input)

        self.login_button = create_button("Login", "primary")
        self.login_button.clicked.connect(self._emit_login_signal)
        form_layout.addWidget(self.login_button)


        self.password_input.returnPressed.connect(self._emit_login_signal)

        outer_layout.addStretch(1)
        outer_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        outer_layout.addStretch(1)

    def _emit_login_signal(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.login_attempted.emit(username, password)

    def show_login_error(self, message):
        QMessageBox.critical(self, "Login Failed", message)



class ReceiptDetailsDialog(QDialog):
    """Modal dialog to display receipt details and optionally delete the receipt."""
    delete_requested = pyqtSignal(str)

    def __init__(self, receipt, parent=None):
        super().__init__(parent)
        self.receipt = receipt or {}
        self.setWindowTitle("Receipt Details")
        self.setFixedSize(600, 420)
        layout = QVBoxLayout(self)

        rid = self.receipt.get('receipt_uuid') or self.receipt.get('id', '')
        id_label = create_label(f"Receipt ID: {rid}", 12, True)
        date_label = create_label(f"Sale Date: {self.receipt.get('sale_date', '')}", 11, False)
        created_at_label = create_label(f"Saved At: {self.receipt.get('created_at', '')}", 10, False)
        total_val = self.receipt.get('total', 0.0)
        total_label = create_label(f"Total: ₱{total_val:.2f}", 12, True)

        # Prepare items text
        items = self.receipt.get('items', [])
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                items = []

        items_text = ""
        if items:
            for it in items:
                name = it.get('name', '-')
                qty = it.get('qty', 0)
                price = it.get('price', 0.0)
                items_text += f"{name} x{qty} @ ₱{price:.2f}\n"
        else:
            items_text = "-"

        items_label = QLabel(items_text)
        items_label.setFont(QFont("Inter", 10))
        items_label.setWordWrap(True)

        btn_row = QHBoxLayout()
        delete_btn = create_button("Delete Receipt", "danger")
        close_btn = create_button("Close", "secondary")
        delete_btn.clicked.connect(self._confirm_and_delete)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(delete_btn)
        btn_row.addWidget(close_btn)

        layout.addWidget(id_label)
        layout.addWidget(date_label)
        layout.addWidget(created_at_label)
        layout.addWidget(items_label)
        layout.addWidget(total_label)
        layout.addLayout(btn_row)

    def _confirm_and_delete(self):
        reply = QMessageBox.question(self, 'Delete Receipt',
                                     "Permanently delete this receipt? This cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            rid = self.receipt.get('receipt_uuid') or self.receipt.get('id')
            if rid is not None:
                self.delete_requested.emit(str(rid))
            self.accept()


class CoffeeShopPOSView(QMainWindow):
    logout_requested = pyqtSignal()
    menu_item_added = pyqtSignal(str, float, int, str)
    menu_item_updated = pyqtSignal(int, str, float, int, str)
    menu_item_deleted = pyqtSignal(int)
    order_item_clicked = pyqtSignal(int)
    remove_order_item_requested = pyqtSignal(int) 
    clear_order_requested = pyqtSignal()
    process_payment_requested = pyqtSignal()
    eod_action_requested = pyqtSignal()
    clear_sales_requested = pyqtSignal()
    retrieve_archived_requested = pyqtSignal()
    password_change_requested = pyqtSignal(str, str, str, str)
    tab_changed = pyqtSignal(str)
    menu_filter_requested = pyqtSignal(str)
    delete_receipt_requested = pyqtSignal(str)

    def __init__(self, initial_role):
        super().__init__()
        self.user_role = initial_role
        self.setWindowTitle("Coffee Shop POS System")
        self.setGeometry(100, 100, 1200, 800)
        self._setup_style()
        self._setup_ui()
        self.stored_categories = []

    def _setup_style(self):
        self.setFont(QFont("Inter", 10))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#F5F5DC'))
        palette.setColor(QPalette.WindowText, QColor('#4A2C2A'))
        self.setPalette(palette)
        self.setStyleSheet("""
            QMainWindow { background-color: #F5F5DC;}
            QTabWidget::pane { border: 1px solid #D2B48C; background-color: #FAF0E6;}
            QTabBar::tab { background: #D2B48C; color: #6F4E37; padding: 10px; border: 1px solid #6F4E37; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px;}
            QTabBar::tab:selected { background: #FAF0E6; color: #4A2C2A; font-weight: bold;}
            QGroupBox { border: 1px solid #D2B48C; border-radius: 8px; margin-top: 10px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; color: #6F4E37; font-weight: bold;}
            QTableWidget { background-color: white; border-radius: 8px; border: 1px solid #D2B48C;}
        """)

    def _setup_ui(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        self.role_label = create_label(f"User Role: {self.user_role}", 12, True)
        header_layout.addWidget(self.role_label)
        header_layout.addStretch(1)
        self.logout_btn = create_button("    🔒     Logout", "secondary")
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        header_layout.addWidget(self.logout_btn)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Inter", 12, QFont.Bold))
        self._create_tabs()

        self.tabs.currentChanged.connect(lambda index: self.tab_changed.emit(self.tabs.tabText(index).strip()))

        central_widget = QWidget()
        main_vbox = QVBoxLayout(central_widget)
        main_vbox.addWidget(header_widget)
        main_vbox.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def _create_tabs(self):
        self.pos_widget = QWidget()
        self._setup_pos_tab()
        self.tabs.addTab(self.pos_widget, "      ☕       Point of Sale")

        self.history_widget = QWidget()
        self._setup_transaction_history_tab()
        self.tabs.addTab(self.history_widget, "      🧾       Transaction History")

        if self.user_role == 'Manager':
            self.admin_widget = QWidget()
            self._setup_admin_tab()
            self.tabs.addTab(self.admin_widget, "      ⚙️       Menu Management")

            self.report_widget = QWidget()
            self._setup_report_tab()
            self.tabs.addTab(self.report_widget, "      📈       Sales Reports")

            self.eod_widget = QWidget()
            self._setup_eod_tab()
            self.tabs.addTab(self.eod_widget, "      💰       End of Day")

            self.settings_widget = QWidget()
            self._setup_settings_tab()
            self.tabs.addTab(self.settings_widget, "      🛠️       Settings")

    def _setup_pos_tab(self):
        main_layout = QHBoxLayout(self.pos_widget)
        main_layout.setSpacing(20)

        menu_box = QVBoxLayout()
        
        header_h = QHBoxLayout()
        title_label = create_label("      ☕       Today's Menu", 16, True)
        title_label.setAlignment(Qt.AlignCenter)
        header_h.addStretch(1)
        header_h.addWidget(title_label)
        header_h.addStretch(1)
        menu_box.addLayout(header_h)

        self.menu_stack = QStackedWidget()
        self.category_page = QWidget() 
        self.item_page = QWidget()     

        
        self._setup_item_page()
    

        self.menu_stack.addWidget(self.category_page)
        self.menu_stack.addWidget(self.item_page)
        self.menu_stack.setCurrentIndex(0) 

        menu_box.addWidget(self.menu_stack)
        menu_box.setStretch(1, 1)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Item", "Price (₱)", "Qty", "Subtotal (₱)"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_table.setSelectionMode(QTableWidget.SingleSelection)
        self.total_label = create_label("TOTAL: ₱0.00", 18, True)

        btn_layout = QHBoxLayout()
        clear_btn = create_button("❌ Remove Selected Item", "secondary")
        clear_btn.clicked.connect(self._handle_remove_order_item)
        clear_all_btn = create_button("Clear All", "secondary")
        clear_all_btn.clicked.connect(self.clear_order_requested.emit)
        checkout_btn = create_button("Process Payment", "primary")
        checkout_btn.clicked.connect(self.process_payment_requested.emit)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(clear_all_btn)
        btn_layout.addWidget(checkout_btn)

        order_box = QVBoxLayout()
        order_box.addWidget(create_label("      🛒       Current Order", 16, True))
        order_box.addWidget(self.order_table)
        order_box.addWidget(self.total_label)
        order_box.addLayout(btn_layout)

        main_layout.addLayout(menu_box, 2)
        main_layout.addLayout(order_box, 1)

    def _setup_item_page(self):
        """Sets up the layout for displaying item cards and the back button."""
        layout = QVBoxLayout(self.item_page)
        
        
        self.back_to_categories_btn = create_button("← Back to Categories", "secondary")
        self.back_to_categories_btn.setFont(QFont("Inter", 12))
        self.back_to_categories_btn.clicked.connect(self._go_back_to_categories)
        
        back_btn_layout = QHBoxLayout()
        back_btn_layout.addWidget(self.back_to_categories_btn)
        back_btn_layout.addStretch(1)
        
        layout.addLayout(back_btn_layout)
        
        
        self.menu_grid_widget = QWidget()
        self.menu_grid_layout = QGridLayout(self.menu_grid_widget)
        self.menu_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(self.menu_grid_widget)
        layout.setStretch(1, 1) 
        
        self.item_page.setLayout(layout)

    
    def _setup_category_page(self, categories):
        """Builds the category selection grid with large buttons."""
        
        if self.category_page.layout() is not None:
             
            QWidget().setLayout(self.category_page.layout())
        
        layout = QGridLayout(self.category_page)
        
        row, col = 0, 0
        max_cols = 2
        
        for category_name in categories:
            
            btn = create_button(category_name, "primary")
            btn.setFont(QFont("Inter", 20, QFont.Bold)) 
            btn.setMinimumSize(250, 150) 
            btn.clicked.connect(lambda _, c=category_name: self.menu_filter_requested.emit(c))
            
            layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.category_page.setLayout(layout)

    
    def _go_back_to_categories(self):
        """Switches the view back to category selection (index 0)."""
        if self.stored_categories:
            self._setup_category_page(self.stored_categories)
        self.menu_stack.setCurrentIndex(0)


    def _handle_remove_order_item(self):
        """Handle removal of selected item from order table."""
        selected_rows = self.order_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an item to remove.")
            return
        
        row = selected_rows[0].row()
        item_name = self.order_table.item(row, 0).text()
        
        if hasattr(self, 'current_order_item_ids') and row < len(self.current_order_item_ids):
            item_id = self.current_order_item_ids[row]
            self.remove_order_item_requested.emit(item_id)

    def _create_menu_card(self, item_id, name, price, stock, category):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        widget.setStyleSheet(f"""
            QWidget {{ background-color: #FFFFFF; border: 2px solid #D2B48C; border-radius: 12px; padding: 10px; margin: 5px;}}
            QWidget:hover {{ border-color: #A0522D;}}
        """)
        widget.setProperty('item_id', item_id)
        widget.mousePressEvent = lambda event: self.order_item_clicked.emit(item_id)

        name_label = create_label(name, 14, True)
        name_label.setAlignment(Qt.AlignCenter)
        price_label = create_label(f"₱{price:.2f}", 12, False)
        price_label.setAlignment(Qt.AlignCenter)
        stock_label = create_label(f"Stock: {stock}", 10, False)
        stock_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(stock_label)
        layout.setSpacing(5)
        return widget

    def update_menu_display(self, menu_items):
        for i in reversed(range(self.menu_grid_layout.count())):
            widget = self.menu_grid_layout.itemAt(i).widget()
            if widget is not None: widget.deleteLater()

        if menu_items:
            self.menu_stack.setCurrentIndex(1)
        
        row, col = 0, 0
        max_cols = 3
        for item_id, name, price, stock, category in menu_items:
            if stock <= 0: continue
            card = self._create_menu_card(item_id, name, price, stock, category)
            self.menu_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def update_pos_filters(self, categories):
        """
        Populate the POS category buttons. 
        This is called initially by the controller on startup and switches to category view.
        """
        
        self.stored_categories = categories
        
    
        self._setup_category_page(categories)
        
        
        self.menu_stack.setCurrentIndex(0)

    def update_order_summary(self, order_data, total):
        self.order_table.setRowCount(0)
        
        self.current_order_item_ids = []

        sorted_keys = sorted(order_data.keys())
        for i, item_id in enumerate(sorted_keys):
            item = order_data[item_id]
            subtotal = item['price'] * item['qty']
            self.current_order_item_ids.append(item_id)  
            self.order_table.insertRow(i)
            self.order_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.order_table.setItem(i, 1, QTableWidgetItem(f"₱{item['price']:.2f}"))
            self.order_table.setItem(i, 2, QTableWidgetItem(str(item['qty'])))
            self.order_table.setItem(i, 3, QTableWidgetItem(f"₱{subtotal:.2f}"))

        self.total_label.setText(f"TOTAL: ₱{total:.2f}")

    def _setup_admin_tab(self):
        main_layout = QHBoxLayout(self.admin_widget)

        form_widget = QGroupBox("Item Details")
        form_layout = QVBoxLayout(form_widget)
        self.id_input = QLineEdit();
        self.id_input.setVisible(False)
        self.name_input = create_input("Item Name")
        self.price_input = create_input("Price (e.g., 250.00)")
        self.stock_input = create_input("Initial Stock (e.g., 100)")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setFont(QFont("Inter", 10))
        self.category_combo.setStyleSheet("padding: 5px;")

        form_layout.addWidget(create_label("Category:", 11, True))
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(create_label("Name:", 11, True));
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(create_label("Price:", 11, True));
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(create_label("Stock:", 11, True));
        form_layout.addWidget(self.stock_input)

        self.add_btn = create_button("      ➕       Add Item", "primary")
        self.update_btn = create_button("      ✏️       Update Selected Item", "secondary")
        self.delete_btn = create_button("      ❌       Delete Selected Item", "secondary")
        self.clear_form_btn = create_button("Clear Form", "secondary")

        self.add_btn.clicked.connect(self._emit_add_item_signal)
        self.update_btn.clicked.connect(self._emit_update_item_signal)
        self.delete_btn.clicked.connect(self._emit_delete_item_signal)
        self.clear_form_btn.clicked.connect(self.clear_crud_form)

        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.update_btn)
        form_layout.addWidget(self.delete_btn)
        form_layout.addWidget(self.clear_form_btn)
        form_layout.addStretch(1)

        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(5)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price (₱)", "Stock"])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.menu_table.clicked.connect(self.load_selected_item_to_form)

        # Right side: search + table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        # search input to filter admin menu table
        self.menu_search_input = create_input("Search menu by name or category")
        # use textChanged signal to filter rows as the user types
        try:
            self.menu_search_input.textChanged.connect(self._filter_admin_menu)
        except Exception:
            # fallback for different Qt versions
            self.menu_search_input.textEdited.connect(self._filter_admin_menu)

        right_layout.addWidget(self.menu_search_input)
        right_layout.addWidget(self.menu_table)

        main_layout.addWidget(form_widget, 1)
        main_layout.addWidget(right_widget, 2)

    def _get_form_data(self):
        name = self.name_input.text().strip()
        category = self.category_combo.currentText().strip()
        price_str = self.price_input.text().strip()
        stock_str = self.stock_input.text().strip()
        item_id_str = self.id_input.text().strip()

        try:
            price = float(price_str)
            stock = int(stock_str)
            item_id = int(item_id_str) if item_id_str else None
        except ValueError:
            return None, "Price must be a number and Stock must be an integer."

        if not name or not category or price <= 0 or stock < 0:
            return None, "Please fill all fields correctly."

        return (item_id, name, price, stock, category), None

    def _emit_add_item_signal(self):
        data, error = self._get_form_data()
        if error:
            QMessageBox.warning(self, "Input Error", error)
            return
        _, name, price, stock, category = data
        self.menu_item_added.emit(name, price, stock, category)

    def _emit_update_item_signal(self):
        data, error = self._get_form_data()
        if error:
            QMessageBox.warning(self, "Input Error", error)
            return
        item_id, name, price, stock, category = data
        if not item_id:
            QMessageBox.warning(self, "Selection Error", "Please select an item to update.")
            return
        self.menu_item_updated.emit(item_id, name, price, stock, category)

    def _emit_delete_item_signal(self):
        item_id_str = self.id_input.text()
        if not item_id_str:
            QMessageBox.warning(self, "Selection Error", "Please select an item to delete.")
            return

        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Item ID {item_id_str}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.menu_item_deleted.emit(int(item_id_str))

    def _filter_admin_menu(self, text):
        """Filter the admin menu table rows by name or category, case-insensitive."""
        if text is None:
            text = ""
        query = text.lower().strip()
        row_count = self.menu_table.rowCount()
        for row in range(row_count):
            try:
                name_item = self.menu_table.item(row, 1)
                cat_item = self.menu_table.item(row, 2)
                name = name_item.text().lower() if name_item and name_item.text() else ""
                cat = cat_item.text().lower() if cat_item and cat_item.text() else ""
                match = (query in name) or (query in cat) if query else True
                self.menu_table.setRowHidden(row, not match)
            except Exception:
                # If anything goes wrong, do not hide the row
                try:
                    self.menu_table.setRowHidden(row, False)
                except Exception:
                    pass

    def update_admin_menu_table(self, items):
        self.menu_table.setRowCount(len(items))
        for row, item in enumerate(items):
            item_id, name, price, stock, category = item
            self.menu_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
            self.menu_table.setItem(row, 1, QTableWidgetItem(name))
            self.menu_table.setItem(row, 2, QTableWidgetItem(category))
            self.menu_table.setItem(row, 3, QTableWidgetItem(f"{price:.2f}"))
            self.menu_table.setItem(row, 4, QTableWidgetItem(str(stock)))

    def update_category_combo(self, categories):
        self.category_combo.clear()
        self.category_combo.addItems(categories + ['New Category...'])
        self.category_combo.setCurrentIndex(0)

    def clear_crud_form(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()
        self.stock_input.clear()
        self.category_combo.setCurrentIndex(0)

    def load_selected_item_to_form(self):
        selected_items = self.menu_table.selectedItems()
        if not selected_items: return
        row = selected_items[0].row()
        self.id_input.setText(self.menu_table.item(row, 0).text())
        self.name_input.setText(self.menu_table.item(row, 1).text())
        self.category_combo.setCurrentText(self.menu_table.item(row, 2).text())
        # Remove peso sign if present
        price_text = self.menu_table.item(row, 3).text().replace('₱', '')
        self.price_input.setText(price_text)
        self.stock_input.setText(self.menu_table.item(row, 4).text())

    def _setup_report_tab(self):
        main_layout = QVBoxLayout(self.report_widget)
        main_layout.addWidget(create_label("      📈       Sales Reports (Last 30 Days)", 16, True))

        top_row_layout = QHBoxLayout()
        self.top_items_canvas = GraphCanvas("Top 5 Selling Items (Quantity)")
        top_row_layout.addWidget(self.top_items_canvas)
        self.category_sales_canvas = GraphCanvas("Revenue Share by Category")
        top_row_layout.addWidget(self.category_sales_canvas)

        self.daily_sales_canvas = GraphCanvas("Daily Revenue Trend")

        main_layout.addLayout(top_row_layout)
        main_layout.addWidget(self.daily_sales_canvas)
        main_layout.addStretch(1)

    def update_report_views(self, sales_df):
        if sales_df.empty:
            self.top_items_canvas.clear_plot("Top 5 Selling Items (Quantity)")
            self.category_sales_canvas.clear_plot("Revenue Share by Category")
            self.daily_sales_canvas.clear_plot("Daily Revenue Trend")
        else:
            self.top_items_canvas.plot_top_selling_items(sales_df)
            self.category_sales_canvas.plot_sales_by_category(sales_df)
            self.daily_sales_canvas.plot_daily_sales(sales_df)

    def _setup_transaction_history_tab(self):
        main_layout = QVBoxLayout(self.history_widget)
        main_layout.addWidget(create_label("      🧾       Transaction History", 16, True))

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Receipt ID", "Date & Time", "Items", "Total (₱)", "Saved At"]) 
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.history_table.cellDoubleClicked.connect(lambda r, c: self._show_receipt_dialog(r))
        main_layout.addWidget(self.history_table)

        btn_row = QHBoxLayout()
        refresh_btn = create_button("Refresh History", "secondary")
        refresh_btn.clicked.connect(lambda: self.tab_changed.emit("Transaction History"))
        btn_row.addWidget(refresh_btn)
        main_layout.addLayout(btn_row)
        main_layout.addStretch(1)

    def update_transaction_history(self, receipts):
        """Receipts should be an iterable of dicts with keys: receipt_uuid, sale_date, items (list), total, created_at"""
        try:
            self.history_receipts = list(receipts)
            self.history_table.setRowCount(len(self.history_receipts))
            for row, r in enumerate(receipts):
                receipt_id = r.get('receipt_uuid') or str(r.get('id', ''))
                sale_date = r.get('sale_date', '')
                items = r.get('items', [])
                if isinstance(items, str):
                    try:
                        items = json.loads(items)
                    except Exception:
                        items = []
                items_str = ", ".join([f"{it.get('name')} x{it.get('qty')}" for it in items]) if items else "-"
                total = r.get('total', 0.0)
                created_at = r.get('created_at', '')

                self.history_table.setItem(row, 0, QTableWidgetItem(receipt_id))
                self.history_table.setItem(row, 1, QTableWidgetItem(sale_date))
                self.history_table.setItem(row, 2, QTableWidgetItem(items_str))
                self.history_table.setItem(row, 3, QTableWidgetItem(f"₱{total:.2f}"))
                self.history_table.setItem(row, 4, QTableWidgetItem(created_at))
        except Exception:
            pass

    def _show_receipt_dialog(self, row=None):
        """Open a modal dialog showing receipt details for the selected row."""
        try:
            if row is None:
                row = self.history_table.currentRow()
            if row < 0:
                return
            receipt = None
            if hasattr(self, 'history_receipts') and row < len(self.history_receipts):
                receipt = self.history_receipts[row]
            if receipt is None:
                QMessageBox.warning(self, "No Data", "Receipt details are not available.")
                return

            dlg = ReceiptDetailsDialog(receipt, parent=self)
            dlg.delete_requested.connect(lambda rid: self.delete_receipt_requested.emit(rid))
            dlg.exec_()
        except Exception:
            pass

    def _setup_eod_tab(self):
        main_layout = QVBoxLayout(self.eod_widget)
        main_layout.setSpacing(15)

        self.simulated_date_display = create_label("", 18, True);
        self.simulated_date_display.setStyleSheet("color: #8B4513;")
        main_layout.addWidget(self.simulated_date_display)
        main_layout.addWidget(create_label("      💰       End of Day Operations & Summary", 18, True))

        summary_group = QGroupBox("Current Day Summary");
        summary_group.setStyleSheet("QGroupBox {background-color: #EDEAE4; border-radius: 10px; padding: 20px;}")
        summary_layout = QGridLayout(summary_group)
        self.eod_date_label = create_label("Report Date: --", 14, True)
        self.eod_rev_label = create_label("Total Revenue: ₱0.00", 16, True)
        self.eod_top_items_label = create_label("Top 3 Sellers:\n-", 12, False)
        self.eod_low_stock_label = create_label("Low Stock Items:\n-", 12, False)
        summary_layout.addWidget(self.eod_date_label, 0, 0, 1, 2)
        summary_layout.addWidget(self.eod_rev_label, 1, 0, 1, 2)
        summary_layout.addWidget(self.eod_top_items_label, 2, 0)
        summary_layout.addWidget(self.eod_low_stock_label, 2, 1)
        main_layout.addWidget(summary_group)

        eod_btn = create_button("      💾       Save EOD & Start Next Day", "primary")
        eod_btn.clicked.connect(self.eod_action_requested.emit)
        main_layout.addWidget(eod_btn)

        retrieve_btn = create_button("      🔁       Retrieve Cleared EOD Records", "secondary")
        retrieve_btn.clicked.connect(self._confirm_retrieve_archived)
        main_layout.addWidget(retrieve_btn)

        main_layout.addWidget(create_label("      📄       Past End of Day Records", 14, True))
        self.past_eod_table = QTableWidget()
        self.past_eod_table.setColumnCount(4)
        self.past_eod_table.setHorizontalHeaderLabels(["Date", "Revenue (₱)", "Top Items", "Low Stock"])
        self.past_eod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.past_eod_table)

        main_layout.addWidget(create_label("      ⚠️       Admin Action: Delete ALL Sales Records", 12, True))
        clear_sales_btn = create_button("      ❌       CLEAR ALL HISTORICAL SALES DATA", "danger")
        clear_sales_btn.clicked.connect(self._prompt_clear_sales_data)
        main_layout.addWidget(clear_sales_btn)
        main_layout.addStretch(1)

    def update_eod_summary_view(self, summary, current_date):
        current_date_str = current_date.strftime('%Y-%m-%d')
        self.simulated_date_display.setText(f"Simulated POS Date: {current_date_str}")
        self.eod_date_label.setText(f"Report Date: {current_date_str}")
        self.eod_rev_label.setText(f"Total Revenue Today: ₱{summary['total_revenue']:.2f}")

        top_items_text = "Top 3 Sellers Today:\n"
        if summary['top_items']:
            for name, qty in summary['top_items']:
                top_items_text += f"- {name} ({qty} units)\n"
        else:
            top_items_text += "No sales recorded today."
        self.eod_top_items_label.setText(top_items_text)

        low_stock_text = "Low Stock Items (<10):\n"
        if summary['low_stock']:
            for name, stock in summary['low_stock']:
                low_stock_text += f"- {name} ({stock} left)\n"
        else:
            low_stock_text += "All items are well stocked (>=10)."
        self.eod_low_stock_label.setText(low_stock_text)

    def update_past_eod_records(self, records):
        self.past_eod_table.setRowCount(len(records))
        for row, record in enumerate(records):
            top_items_str = ", ".join([f"{name} ({qty})" for name, qty in record['top_items']]) or "None"
            low_stock_str = ", ".join([f"{name} ({stock})" for name, stock in record['low_stock']]) or "None"

            self.past_eod_table.setItem(row, 0, QTableWidgetItem(record['date']))
            self.past_eod_table.setItem(row, 1, QTableWidgetItem(f"₱{record['revenue']:.2f}"))
            self.past_eod_table.setItem(row, 2, QTableWidgetItem(top_items_str))
            self.past_eod_table.setItem(row, 3, QTableWidgetItem(low_stock_str))

    def _prompt_clear_sales_data(self):
        reply = QMessageBox.critical(self, 'DANGER! Clear All Data',
                                     "This action will permanently delete **ALL historical sales records AND ALL saved EOD summaries**. Are you absolutely sure you want to proceed?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_sales_requested.emit()

    def _confirm_retrieve_archived(self):
        reply = QMessageBox.question(self, 'Retrieve Archived Records',
                                     "Restore archived End-Of-Day summaries that were previously archived before clearing?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.retrieve_archived_requested.emit()

    def _setup_settings_tab(self):
        main_layout = QVBoxLayout(self.settings_widget)
        main_layout.setSpacing(20)

        main_layout.addWidget(create_label("      🛠️       User & System Settings", 16, True))

        password_group = QGroupBox("Change User Password (Manager Only)")
        password_layout = QVBoxLayout(password_group)

        self.pass_username_combo = QComboBox()
        self.pass_username_combo.setFont(QFont("Inter", 10))

        self.old_password_input = create_input("Old Password", is_password=True)
        self.new_password_input = create_input("New Password", is_password=True)
        self.confirm_password_input = create_input("Confirm New Password", is_password=True)

        change_pass_btn = create_button("Update Password", "primary")
        change_pass_btn.clicked.connect(self._emit_change_password_signal)

        password_layout.addWidget(create_label("User to change:", 11, True))
        password_layout.addWidget(self.pass_username_combo)
        password_layout.addWidget(create_label("Old Password:", 11, True))
        password_layout.addWidget(self.old_password_input)
        password_layout.addWidget(create_label("New Password:", 11, True))
        password_layout.addWidget(self.new_password_input)
        password_layout.addWidget(create_label("Confirm New Password:", 11, True))
        password_layout.addWidget(self.confirm_password_input)
        password_layout.addWidget(change_pass_btn)

        main_layout.addWidget(password_group)
        main_layout.addStretch(1)

    def update_password_combo(self, usernames):
        self.pass_username_combo.clear()
        self.pass_username_combo.addItems(usernames)

    def _emit_change_password_signal(self):
        username = self.pass_username_combo.currentText().strip()
        old_pass = self.old_password_input.text().strip()
        new_pass = self.new_password_input.text().strip()
        confirm_pass = self.confirm_password_input.text().strip()

        if not all([username, old_pass, new_pass, confirm_pass]):
            QMessageBox.warning(self, "Input Error", "All password fields must be filled.")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Input Error", "New password and confirmation do not match.")
            return

        self.password_change_requested.emit(username, old_pass, new_pass, confirm_pass)

    def clear_password_fields(self):
        self.old_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
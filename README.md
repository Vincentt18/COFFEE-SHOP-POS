# Coffee Shop POS System

A desktop Point of Sale (POS) system for managing coffee shop operations, built with Python and PyQt5.

## Features

- **User Authentication**: Secure login system with role-based access control
- **Menu Management**: Easy management of menu items and pricing
- **Order Processing**: Create and process customer orders
- **Database Management**: SQLite database for persistent data storage
- **Reporting**: Generate sales and inventory reports using pandas
- **Password Management**: Secure password update functionality

## Project Structure

- **main.py** - Entry point for the application
- **model.py** - Application data model and business logic
- **view.py** - User interface components (PyQt5)
- **controller.py** - Event handling and application control
- **database.py** - Database management and queries
- **test_all.py** - Unit tests
- **coffee_pos.db** - SQLite database file (auto-created)

## Requirements

- Python 3.7+
- PyQt5
- pandas
- sqlite3 (included with Python)

## Installation

1. Install required dependencies:
pip install PyQt5 pandas

2. Run the application:
python main.py

## Usage

1. Launch the application using `python main.py`
2. Log in with your credentials
3. Navigate through the interface to manage orders, menu items, and inventory
4. Generate reports as needed

## Database

The application uses SQLite for data persistence. The database file (`coffee_pos.db`) is automatically created on first run with the necessary tables for users, menu items, orders, and inventory.

## Notes

- Ensure the pandas library is installed for reporting features to work correctly
- The application uses the "Inter" font family for the UI

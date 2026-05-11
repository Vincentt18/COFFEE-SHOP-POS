import sys
try:
    import pandas as pd
except ImportError:
    print("Error: The 'pandas' library is required for reporting features. Please run 'pip install pandas'")
    sys.exit(1)
try:
    import json
except ImportError:
    print("Error: The 'json' library is required.")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from model import AppModel
from controller import AppController

if __name__ == '__main__':
    app = QApplication(sys.argv)

    font = QFont("Inter")
    app.setFont(font)
    model = AppModel()

    controller = AppController(model, app)

    sys.exit(app.exec_())

    
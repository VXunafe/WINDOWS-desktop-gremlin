
import sys
from PySide6.QtWidgets import QApplication

import config_manager
from gremlin import GremlinWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # please load configuration files before creating the main window
    try:
        config_manager.load_master_config()
        config_manager.load_config_char()
    except Exception as e:
        print(f"Fatal Error: Could not load configuration. {e}")
        sys.exit(1)

    window = GremlinWindow()
    window.show()
    sys.exit(app.exec())

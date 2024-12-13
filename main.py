import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.config_manager import ConfigManager
import logging

def main():
    # 初始化配置
    config = ConfigManager()
    
    # 设置应用信息
    app = QApplication(sys.argv)
    app.setApplicationName(config.get('app', 'name'))
    app.setApplicationVersion(config.get('app', 'version'))
    
    try:
        window = MainWindow(config)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main() 
import unittest
from PyQt6.QtWidgets import QApplication
import sys
from gui.main_window import MainWindow
from utils.config_manager import ConfigManager

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """在所有测试前创建QApplication实例"""
        cls.app = QApplication(sys.argv)
        cls.config = ConfigManager()
    
    def setUp(self):
        """每个测试前创建新的窗口"""
        self.window = MainWindow(self.config)
    
    def test_window_title(self):
        """测试窗口标题"""
        expected_title = self.config.get('ui', 'window', 'title')
        self.assertEqual(self.window.windowTitle(), expected_title)
    
    def test_window_size(self):
        """测试窗口尺寸"""
        expected_width = self.config.get('ui', 'window', 'width')
        expected_height = self.config.get('ui', 'window', 'height')
        self.assertEqual(self.window.width(), expected_width)
        self.assertEqual(self.window.height(), expected_height)

if __name__ == '__main__':
    unittest.main() 
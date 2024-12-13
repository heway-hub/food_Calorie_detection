import unittest
from pathlib import Path
import shutil
from utils.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 备份现有的配置文件（如果存在）
        self.config_path = Path("config.yaml")
        self.backup_path = Path("config.yaml.bak")
        if self.config_path.exists():
            shutil.copy(self.config_path, self.backup_path)
            self.config_path.unlink()  # 删除原配置文件
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原配置文件
        if self.backup_path.exists():
            shutil.copy(self.backup_path, self.config_path)
            self.backup_path.unlink()
    
    def test_singleton(self):
        """测试单例模式"""
        config1 = ConfigManager()
        config2 = ConfigManager()
        self.assertIs(config1, config2)
    
    def test_default_config(self):
        """测试默认配置创建"""
        config = ConfigManager()
        self.assertEqual(config.get('app', 'name'), 'NutriScan')
        self.assertEqual(config.get('app', 'version'), '1.0.0')
    
    def test_directory_creation(self):
        """测试必要目录创建"""
        config = ConfigManager()
        paths = [
            Path(config.get('storage', 'images', 'path')),
            Path(config.get('storage', 'logs', 'path')),
            Path(config.get('temp', 'path')),
            Path(config.get('database', 'backup_dir'))
        ]
        
        for path in paths:
            self.assertTrue(path.exists())
    
    def test_config_modification(self):
        """测试配置修改"""
        config = ConfigManager()
        test_value = "test_value"
        config.set(test_value, 'test', 'key')
        self.assertEqual(config.get('test', 'key'), test_value)

if __name__ == '__main__':
    unittest.main() 
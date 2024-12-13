# utils/config_manager.py
import yaml
import logging
from pathlib import Path
from typing import Any, Optional, Dict

class ConfigManager:
    """配置管理器单例类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'config'):
            self.config_path = Path("config.yaml")
            self.config = self._load_config()
            self._setup_logging()
            self._ensure_directories()
    
    def _load_config(self) -> Dict:
        """加载配置文件，如果不存在则创建默认配置"""
        try:
            if not self.config_path.exists():
                return self._create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认配置文件"""
        default_config = {
            'app': {
                'name': 'NutriScan',
                'version': '1.0.0',
                'debug': False
            },
            'database': {
                'type': 'sqlite',
                'path': 'sqlite:///nutriscan.db',
                'backup_dir': './backup/database'
            },
            'storage': {
                'images': {
                    'path': './resources/images',
                    'allowed_types': ['.jpg', '.jpeg', '.png'],
                    'max_size': 5242880,
                    'thumbnail_size': [200, 200]
                },
                'logs': {
                    'path': './logs',
                    'level': 'INFO',
                    'max_size': 10485760,
                    'backup_count': 5
                }
            },
            'ui': {
                'window': {
                    'title': 'NutriScan',
                    'width': 800,
                    'height': 600,
                    'min_width': 600,
                    'min_height': 400,
                    'icon': './resources/icons/app.ico'
                },
                'theme': {
                    'name': 'default',
                    'style_sheet': './resources/styles/default.qss',
                    'primary_color': '#2196F3',
                    'secondary_color': '#FFC107'
                }
            },
            'temp': {
                'path': './temp',
                'cleanup_on_exit': True
            }
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict) -> None:
        """保存配置到文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    
    def _setup_logging(self) -> None:
        """设置日志配置"""
        log_config = self.get('storage', 'logs')
        if log_config:
            Path(log_config['path']).mkdir(parents=True, exist_ok=True)
            logging.basicConfig(
                filename=str(Path(log_config['path']) / 'app.log'),
                level=getattr(logging, log_config['level']),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        paths = [
            self.get('storage', 'images', 'path'),
            self.get('storage', 'logs', 'path'),
            self.get('temp', 'path'),
            self.get('database', 'backup_dir')
        ]
        
        for path in paths:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """获取配置项，支持多级键"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
    
    def set(self, value: Any, *keys: str) -> None:
        """设置配置项，支持多级键"""
        if not keys:
            return
        
        config = self.config
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        
        config[keys[-1]] = value
        self._save_config(self.config)
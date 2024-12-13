class Colors:
    # 主色调
    PRIMARY = "#1890ff"      # 主要蓝色
    PRIMARY_LIGHT = "#e6f7ff"  # 浅蓝色背景
    PRIMARY_DARK = "#0050b3"   # 深蓝色
    
    # 辅助色
    BG = "#f0f2f5"          # 背景灰色
    WHITE = "#ffffff"        # 纯白色
    BORDER = "#d9d9d9"       # 边框灰色
    TEXT = "#333333"         # 主要文本
    TEXT_SECONDARY = "#666666"  # 次要文本
    TEXT_HINT = "#999999"      # 提示文本
    
    # 强调色
    ACCENT = "#fa8c16"       # 橙色（主要操作）
    SUCCESS = "#52c41a"      # 绿色（成功）
    WARNING = "#faad14"      # 黄色（警告）
    ERROR = "#f5222d"        # 红色（错误）

class Fonts:
    # 字体族
    FAMILY = "Microsoft YaHei"
    
    # 字号定义
    TITLE = 20        # 主标题
    SUBTITLE = 16     # 副标题
    HEADING = 14      # 标题
    CONTENT = 12      # 正文
    SMALL = 10        # 小字
    MINI = 9         # 最小字

class StyleSheet:
    @staticmethod
    def get_main_window_style():
        return f"""
            /* 全局字体设置 */
            * {{
                font-family: "{Fonts.FAMILY}";
            }}
            
            /* 主窗口 */
            QMainWindow {{
                background-color: {Colors.BG};
            }}
            
            /* 标题标签 */
            QLabel[title="true"] {{
                font-size: {Fonts.TITLE}px;
                font-weight: bold;
                color: {Colors.TEXT};
                padding: 10px;
            }}
            
            /* 副标题标签 */
            QLabel[subtitle="true"] {{
                font-size: {Fonts.SUBTITLE}px;
                font-weight: bold;
                color: {Colors.TEXT};
                padding: 8px;
            }}
            
            /* 普通标签 */
            QLabel {{
                font-size: {Fonts.CONTENT}px;
                color: {Colors.TEXT};
            }}
            
            /* 工具栏按钮基础样式 - 扁平化设计 */
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT};
                border: none;  /* 移除边框实现扁平化 */
                border-radius: 6px;
                padding: 8px 20px;
                font-size: {Fonts.CONTENT}px;
                font-weight: 500;  /* 稍微加粗 */
                min-width: 80px;
                margin: 0 4px;  /* 按钮间距 */
                transition: all 0.3s;  /* 添加过渡效果 */
            }}
            
            /* 悬停效果 */
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
                color: {Colors.PRIMARY};
                transform: translateY(-1px);  /* 轻微上浮效果 */
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* 添加阴影 */
            }}
            
            /* 点击效果 */
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY};
                color: {Colors.WHITE};
                transform: translateY(1px);  /* 轻微下沉效果 */
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);  /* 减小阴影 */
            }}
            
            /* 禁用状态 */
            QPushButton:disabled {{
                background-color: {Colors.BG};
                color: {Colors.TEXT_HINT};
                border: none;
                box-shadow: none;
            }}
            
            /* 开始分析按钮特殊样式 */
            QPushButton#analyze_btn {{
                background-color: {Colors.ACCENT};
                color: {Colors.WHITE};
                font-weight: bold;
                padding: 8px 24px;  /* 稍微加大内边距 */
            }}
            
            QPushButton#analyze_btn:hover {{
                background-color: {Colors.PRIMARY};
                box-shadow: 0 4px 8px rgba(24, 144, 255, 0.2);  /* 特殊阴影效果 */
            }}
            
            QPushButton#analyze_btn:pressed {{
                background-color: {Colors.PRIMARY_DARK};
                box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
            }}
            
            /* 保存按钮特殊样式 */
            QPushButton#save_btn {{
                background-color: {Colors.SUCCESS};
                color: {Colors.WHITE};
                font-weight: bold;
            }}
            
            QPushButton#save_btn:hover {{
                background-color: {Colors.PRIMARY};
                box-shadow: 0 4px 8px rgba(82, 196, 26, 0.2);
            }}
            
            QPushButton#save_btn:pressed {{
                background-color: {Colors.PRIMARY_DARK};
                box-shadow: 0 2px 4px rgba(82, 196, 26, 0.2);
            }}
            
            /* 预览区域 */
            QLabel#preview_area {{
                background-color: {Colors.WHITE};
                border: 2px dashed {Colors.BORDER};
                border-radius: 8px;
                padding: 20px;
            }}
            
            /* 结果显示区域 */
            QLabel#result_label {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 16px;
                color: {Colors.TEXT};
            }}
            
            /* 状态栏 */
            QStatusBar {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_SECONDARY};
                border-top: 1px solid {Colors.BORDER};
            }}
            
            /* 表格样式 */
            QTableWidget {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                gridline-color: {Colors.BORDER};
                font-size: {Fonts.CONTENT}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {Colors.TEXT};
            }}
            QTableWidget::item:selected {{
                background-color: {Colors.PRIMARY_LIGHT};
                color: {Colors.PRIMARY};
            }}
            
            /* 对话框样式 */
            QDialog {{
                background-color: {Colors.WHITE};
                font-size: {Fonts.CONTENT}px;
            }}
            
            /* 标签样式 */
            QLabel {{
                color: {Colors.TEXT};
            }}
            
            /* 输入框样式 */
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                color: {Colors.TEXT};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {Colors.PRIMARY};
            }}
        """ 

    @staticmethod
    def get_dialog_style():
        """获取对话框样式"""
        return f"""
            QDialog {{
                background-color: {Colors.WHITE};
                font-family: "{Fonts.FAMILY}";
            }}
            
            QLabel {{
                color: {Colors.TEXT};
                font-size: {Fonts.CONTENT}px;
            }}
            
            QLabel[heading="true"] {{
                font-size: {Fonts.HEADING}px;
                font-weight: bold;
                padding: 10px 0;
            }}
        """
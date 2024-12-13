import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口基本属性
        self.setWindowTitle("食物卡路里检测")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏部分
        toolbar_layout = QHBoxLayout()
        self.upload_btn = QPushButton("上传图片")
        self.analyze_btn = QPushButton("开始分析")
        self.history_btn = QPushButton("历史记录")
        
        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.analyze_btn)
        toolbar_layout.addWidget(self.history_btn)
        toolbar_layout.addStretch()  # 添加弹性空间
        
        # 创建内容区域
        content_layout = QHBoxLayout()
        
        # 左侧预览区域
        self.preview_area = QLabel("图片预览区域")
        self.preview_area.setMinimumSize(400, 400)
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setStyleSheet("border: 2px dashed gray;")
        
        # 右侧结果区域
        result_layout = QVBoxLayout()
        self.result_label = QLabel("分析结果")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.save_btn = QPushButton("保存记录")
        
        result_layout.addWidget(self.result_label)
        result_layout.addStretch()
        result_layout.addWidget(self.save_btn)
        
        # 添加到内容布局
        content_layout.addWidget(self.preview_area)
        content_layout.addLayout(result_layout)
        
        # 将所有布局添加到主布局
        main_layout.addLayout(toolbar_layout)
        main_layout.addLayout(content_layout)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 连接信号和槽
        self.upload_btn.clicked.connect(self.upload_image)
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.history_btn.clicked.connect(self.show_history)
        self.save_btn.clicked.connect(self.save_record)
        
        # 初始状态设置
        self.analyze_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

    def upload_image(self):
        # TODO: 实现图片上传功能
        self.statusBar.showMessage("上传图片...")
        self.analyze_btn.setEnabled(True)

    def analyze_image(self):
        # TODO: 实现图片分析功能
        self.statusBar.showMessage("分析中...")
        self.save_btn.setEnabled(True)

    def show_history(self):
        # TODO: 实现历史记录显示功能
        self.statusBar.showMessage("显示历史记录...")

    def save_record(self):
        # TODO: 实现保存记录功能
        self.statusBar.showMessage("保存记录...")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NutriScan")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 添加上传按钮
        self.upload_btn = QPushButton("上传食物图片")
        self.upload_btn.clicked.connect(self.upload_image)
        
        # 添加图片预览标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 2px dashed gray")
        
        # 将部件添加到布局中
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.image_label)
    
    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_name:
            # TODO: 实现图片处理逻辑
            pass 
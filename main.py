import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QStatusBar, 
                            QFileDialog, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
from models import AIAnalyzer
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.analyzer = None
        self.db_manager = DatabaseManager()
        self.init_ui()
        
        # 确保images目录存在
        if not os.path.exists('images'):
            os.makedirs('images')

    def init_ui(self):
        # 设置窗口基本属性
        self.setWindowTitle("食物卡路里检测")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具���部分
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
        """处理图片上传功能"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)"
        )
        
        if file_name:
            try:
                print(f"\n选择的图片文件: {file_name}")
                
                # 保存原始图片路径
                self.current_image_path = file_name
                
                # 使用PIL打开图片进行处理
                with Image.open(file_name) as img:
                    # 打印图片信息
                    print(f"原始图片大小: {img.size}")
                    print(f"图片格式: {img.format}")
                    print(f"图片模式: {img.mode}")
                    
                    # 调整图片大小以适应预览区域
                    preview_size = (400, 400)
                    img.thumbnail(preview_size, Image.Resampling.LANCZOS)
                    print(f"缩略图大小: {img.size}")
                    
                    # 保存处理后的图片到images目录
                    save_path = os.path.join('images', os.path.basename(file_name))
                    img.save(save_path)
                    print(f"保存预览图片到: {save_path}")
                    
                    # 转换为QPixmap并显示
                    pixmap = QPixmap(save_path)
                    self.preview_area.setPixmap(pixmap)
                    self.preview_area.setScaledContents(True)
                
                # 更新状态
                self.statusBar.showMessage(f"图片已上传: {os.path.basename(file_name)}")
                self.analyze_btn.setEnabled(True)
                
            except Exception as e:
                error_msg = f"图片处理失败: {str(e)}"
                print(f"错误: {error_msg}")
                QMessageBox.critical(self, "错误", error_msg)
                self.statusBar.showMessage("图片上传失败")
                return
    
    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        if hasattr(self, 'preview_area') and self.preview_area.pixmap():
            # 保持图片纵横比
            pixmap = self.preview_area.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.preview_area.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_area.setPixmap(scaled_pixmap)

    def analyze_image(self):
        """处理图片分析功能"""
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先上传图片")
            return

        # 创建进度对话框
        self.progress_dialog = QProgressDialog("正在分析图片...", "取消", 0, 0, self)
        self.progress_dialog.setWindowTitle("分析中")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.show()

        # 创建并启动分析线程
        self.analyzer = AIAnalyzer(self.current_image_path)
        self.analyzer.analysis_complete.connect(self.handle_analysis_result)
        self.analyzer.analysis_error.connect(self.handle_analysis_error)
        self.analyzer.finished.connect(self.progress_dialog.close)
        self.analyzer.start()

    def handle_analysis_result(self, result):
        """处理分析结果"""
        try:
            # 解析JSON数据
            json_result = json.loads(result)  # 这里的result已经是有效的JSON字符串
            
            # 格式化显示结果
            display_text = self.format_result_for_display(json_result)
            self.result_label.setText(display_text)
            
            # 保存到数据库
            try:
                record_id = self.db_manager.save_analysis_result(
                    self.current_image_path, 
                    json_result  # 直接传入解析后的数据
                )
                self.statusBar.showMessage(f"分析完成，记录ID: {record_id}")
            except Exception as e:
                print(f"保存数据失败: {str(e)}")
                self.statusBar.showMessage("分析完成，但保存失败")
            
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            self.handle_analysis_error(f"结果解析失败: {str(e)}")

    def format_result_for_display(self, result):
        """格式化结果用于显示"""
        text = []
        text.append("=== 分析结果 ===\n")
        
        for food in result.get('foods', []):
            text.append(f"食物: {food.get('name')}")
            text.append(f"类别: {food.get('category')}")
            text.append(f"重量: {food.get('weight')}克")
            text.append(f"卡路里: {food.get('calories')}卡路里\n")
            
            text.append("营养成分:")
            nutrition = food.get('nutrition', {})
            text.append(f"- 蛋白质: {nutrition.get('protein')}克")
            text.append(f"- 脂肪: {nutrition.get('fat')}克")
            text.append(f"- 碳水化合物: {nutrition.get('carbohydrates')}克")
            text.append(f"- 膳食纤维: {nutrition.get('fiber')}克")
            text.append(f"- 钠: {nutrition.get('sodium')}毫克\n")
        
        text.append(f"\n总卡路里: {result.get('total_calories')}")
        text.append(f"餐点类型: {result.get('meal_category')}")
        text.append(f"\n健康建议: {result.get('health_tips')}")
        
        return "\n".join(text)

    def handle_analysis_error(self, error_message):
        """处理分析错误"""
        QMessageBox.critical(self, "错误", f"分析失败: {error_message}")
        self.statusBar.showMessage("分析失败")
        self.progress_dialog.close()

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
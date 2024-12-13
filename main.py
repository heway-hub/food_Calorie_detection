import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QStatusBar, 
                            QFileDialog, QMessageBox, QProgressDialog, 
                            QDialog, QTableWidget, QTableWidgetItem, 
                            QComboBox, QDateEdit, QDoubleSpinBox, QLineEdit, 
                            QDialogButtonBox, QFormLayout, QGroupBox, 
                            QHeaderView, QMenu)
from PyQt6.QtCore import Qt, QDate, QThread
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
from models import AIAnalyzer
from database import DatabaseManager
from datetime import datetime, timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from styles import Colors, StyleSheet

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.style.use('seaborn')  # 使用更现代的样式

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.analyzer = None
        self.db_manager = DatabaseManager()
        self.batch_images = []  # 添加批量图片列表
        
        # 应用样式表
        self.setStyleSheet(StyleSheet.get_main_window_style())
        
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
        
        # 创建工具部分
        toolbar_layout = QHBoxLayout()
        self.stats_btn = QPushButton("每日统计")
        self.upload_btn = QPushButton("上传图片")
        self.batch_import_btn = QPushButton("批量导入")
        self.analyze_btn = QPushButton("开始分析")
        self.history_btn = QPushButton("历史记录")
        
        # 设置按钮对象名
        self.analyze_btn.setObjectName("analyze_btn")
        
        # 设置按钮工具提示
        self.stats_btn.setToolTip("查看每日营养摄入统计")
        self.upload_btn.setToolTip("上传单张食物图片")
        self.batch_import_btn.setToolTip("批量导入多张图片")
        self.analyze_btn.setToolTip("开始分析食物图片")
        self.history_btn.setToolTip("查看历史记录")
        
        toolbar_layout.addWidget(self.stats_btn)
        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.batch_import_btn)
        toolbar_layout.addWidget(self.analyze_btn)
        toolbar_layout.addWidget(self.history_btn)
        toolbar_layout.addStretch()  # 添加弹性空间
        
        # 创建内容区域
        content_layout = QHBoxLayout()
        
        # 左侧预览区域
        self.preview_area = QLabel("图片预览区域")
        self.preview_area.setMinimumSize(400, 400)
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setObjectName("preview_area")
        
        # 设置预览区域标签属性
        self.preview_area.setProperty("heading", True)
        
        # 右侧结果区域
        result_layout = QVBoxLayout()
        self.result_label = QLabel("分析结果")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        result_layout.addWidget(self.result_label)
        result_layout.addStretch()
        
        # 设置结果区域标签属性
        self.result_label.setProperty("heading", True)
        
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
        self.stats_btn.clicked.connect(self.show_statistics)
        self.batch_import_btn.clicked.connect(self.batch_import_images)
        
        # 初始状态设置
        self.analyze_btn.setEnabled(False)
        
        # 设置按钮对象名
        self.analyze_btn.setObjectName("analyze_btn")
        self.preview_area.setObjectName("preview_area")
        self.result_label.setObjectName("result_label")

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
                
                # 保存原始图片径
                self.current_image_path = file_name
                
                # 使用PIL打开图片行处理
                with Image.open(file_name) as img:
                    # 打印图片息
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
            # 保持图片纵比
            pixmap = self.preview_area.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.preview_area.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_area.setPixmap(scaled_pixmap)

    def analyze_image(self):
        """处理图片分析功能"""
        if self.batch_images:  # 如果有批量图片待理
            self.analyze_batch_images()
        elif self.current_image_path:  # 单张图片处理
            self.analyze_single_image()
        else:
            QMessageBox.warning(self, "警告", "请先上传图片")

    def analyze_batch_images(self):
        """处理批量图片分析"""
        if not self.batch_images:
            return
        
        # 创建进度对话框
        progress = QProgressDialog(
            "正在处理图片...", 
            "取消", 
            0, 
            len(self.batch_images), 
            self
        )
        progress.setWindowTitle("批量处理")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        success_count = 0  # 成功处理的图片计数
        
        # 处理每张图片
        for i, image_path in enumerate(self.batch_images):
            if progress.wasCanceled():
                break
            
            progress.setLabelText(f"正在处理: {os.path.basename(image_path)}")
            progress.setValue(i)
            
            try:
                # 复制图片到应用目录
                filename = os.path.basename(image_path)
                new_path = os.path.join('images', f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
                
                # 确保目标路径唯一
                base, ext = os.path.splitext(new_path)
                counter = 1
                while os.path.exists(new_path):
                    new_path = f"{base}_{counter}{ext}"
                    counter += 1
                
                # 复制并处理图片
                Image.open(image_path).save(new_path)
                
                # 更新界面显示
                self.current_image_path = new_path
                self.display_image(new_path)
                QApplication.processEvents()
                
                # 分析图片
                analyzer = AIAnalyzer(new_path)
                try:
                    result = analyzer.analyze_image_sync()
                    if result:
                        try:
                            # 解析JSON字符串
                            json_result = json.loads(result) if isinstance(result, str) else result
                            # 保存分析结果到数据库
                            record_id = self.db_manager.save_analysis_result(new_path, json_result)
                            if record_id:
                                success_count += 1
                        except Exception as e:
                            print(f"保存数据失败: {str(e)}")
                            QMessageBox.warning(
                                self,
                                "保存失败",
                                f"图片 {filename} 的分析结果保存失败: {str(e)}"
                            )
                except Exception as e:
                    print(f"分析失败: {str(e)}")
                    QMessageBox.warning(
                        self,
                        "分析失败",
                        f"片 {filename} 分析失败: {str(e)}"
                    )
                
                QApplication.processEvents()
                QThread.msleep(1000)
                
            except Exception as e:
                print(f"处理图片失败: {str(e)}")
                QMessageBox.warning(
                    self,
                    "处理失败",
                    f"处理图片 {filename} 时出错: {str(e)}"
                )
        
        progress.setValue(len(self.batch_images))
        
        # 显示完成消息
        QMessageBox.information(
            self,
            "完成",
            f"批量处理完成\n成功处理: {success_count}/{len(self.batch_images)} 张图片"
        )
        
        # 清空图片列表
        self.batch_images = []
        
        # 刷新历史记录
        if hasattr(self, 'history_dialog') and self.history_dialog.isVisible():
            self.history_dialog.update_table()

    def analyze_single_image(self):
        """处理单张图片分析"""
        if not self.current_image_path:
            return
        
        try:
            # 创建进度对话框
            self.progress_dialog = QProgressDialog(
                "正在分析图片...", 
                "取消", 
                0, 
                100, 
                self
            )
            self.progress_dialog.setWindowTitle("分析中")
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)
            
            # 更新状态
            self.statusBar.showMessage("正在分析图片...")
            
            # 创建分析器实例
            self.analyzer = AIAnalyzer(self.current_image_path)
            
            try:
                # 同步分析图片
                result = self.analyzer.analyze_image_sync()
                
                if result:
                    # 解析JSON字符串
                    json_result = json.loads(result) if isinstance(result, str) else result
                    
                    # 显示分析结果
                    self.display_result(json_result)
                    
                    # 保存分析结果到数据库并更新状态栏
                    record_id = self.db_manager.save_analysis_result(
                        self.current_image_path, 
                        json_result
                    )
                    
                    if record_id:
                        self.statusBar.showMessage("分析完成，结果已自动保存")
                    else:
                        self.statusBar.showMessage("分析完成，但保存失败")
                        
                else:
                    self.handle_analysis_error("分析结果为空")
                    
            except Exception as e:
                self.handle_analysis_error(str(e))
                
            finally:
                self.progress_dialog.close()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析过程出错: {str(e)}")
            self.statusBar.showMessage("分析失败")

    def display_result(self, result):
        """格式化结果用于显示"""
        text = []
        text.append("=== 分析结果 ===\n")
        
        for food in result.get('foods', []):
            text.append(f"食物: {food.get('name', '未知')}\n")
            text.append(f"重量: {food.get('weight', 0)}g\n")
            text.append(f"卡路里: {food.get('calories', 0)} kcal\n")
            
            # 显示营养成分
            nutrition = food.get('nutrition', {})
            text.append("营养成分:\n")
            text.append(f"  - 蛋白质: {nutrition.get('protein', 0)}g\n")
            text.append(f"  - 脂肪: {nutrition.get('fat', 0)}g\n")
            text.append(f"  - 碳水化合物: {nutrition.get('carbohydrates', 0)}g\n")
            text.append(f"  - 膳食纤维: {nutrition.get('fiber', 0)}g\n")
            text.append(f"  - 钠: {nutrition.get('sodium', 0)}mg\n")
            text.append("\n")
        
        # 显示总卡路里
        text.append(f"\n总卡路里: {result.get('total_calories', 0)} kcal\n")
        
        # 显示健康建议
        if 'health_tips' in result:
            text.append(f"\n健康建议:\n{result['health_tips']}\n")
        
        self.result_label.setText("".join(text))

    def handle_analysis_error(self, error_message):
        """处理分析错误"""
        QMessageBox.critical(self, "错误", f"分析失败: {error_message}")
        self.statusBar.showMessage("分析失败")
        self.progress_dialog.close()

    def show_history(self):
        """显示历史记录对话框"""
        self.history_dialog = HistoryDialog(self.db_manager, self)
        self.history_dialog.exec()

    def show_statistics(self):
        """显示每日统计对话框"""
        dialog = DailyStatisticsDialog(self.db_manager, self)
        dialog.exec()

    def display_image(self, image_path):
        """显示图片"""
        try:
            # 使用PIL打开图片进行处理
            with Image.open(image_path) as img:
                # 调整图片大小以适应预览区域
                preview_size = (400, 400)
                img.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
                # 转换为QPixmap并显示
                if img.mode == "RGBA":
                    # 处理RGBA图片
                    data = img.tobytes("raw", "RGBA")
                    qim = QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
                else:
                    # 处理其他格式图片
                    data = img.tobytes("raw", "RGB")
                    qim = QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGB888)
                
                pixmap = QPixmap.fromImage(qim)
                self.preview_area.setPixmap(pixmap)
                self.preview_area.setScaledContents(True)
                
        except Exception as e:
            print(f"显示图片失败: {str(e)}")
            self.preview_area.setText("图片显示失败")

    def batch_import_images(self):
        """批量导入图片"""
        # 选择文件夹
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择图片文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            return
        
        # 获取文件夹中的所有图片文件
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        self.batch_images = []  # 清空之前的批量图片列表
        
        for file in os.listdir(folder_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                self.batch_images.append(os.path.join(folder_path, file))
        
        if not self.batch_images:
            QMessageBox.warning(self, "警告", "所选文件夹中没有找到有效的图片文件")
            return
        
        # 显示导入信息
        import_info = [
            "<h3>已导入以下图片：</h3>",
            "<ul style='margin-left: 20px'>"
        ]
        for img_path in self.batch_images:
            import_info.append(f"<li>{os.path.basename(img_path)}</li>")
        import_info.append("</ul>")
        import_info.append(f"<p>共 {len(self.batch_images)} 张图片</p>")
        import_info.append('<p>点击"开始分析"按钮开始处理</p>')
        
        # 在结果区域显示导入信息
        self.result_label.setText("".join(import_info))
        
        # 更新状态
        self.statusBar.showMessage(f"已导入 {len(self.batch_images)} 张图片，等待分析")
        self.analyze_btn.setEnabled(True)

class HistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("历史记录")
        self.setMinimumSize(1000, 600)  # 增加窗口宽度
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # 增加布局间距
        
        # 创建表格 - 移到前面
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "日期", "时间", "食物", "重量(g)", "卡路里(kcal)"
        ])
        
        # 设置表格属性
        self.setup_table_properties()
        
        # 修改表格选择模式为多选
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # 添加选择变化信号连接
        self.table.itemSelectionChanged.connect(self.update_batch_delete_button)
        
        # 创建筛选区域
        filter_group = QGroupBox("筛选选项")
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        filter_layout.setSpacing(20)  # 增加组件间距
        
        # 日期选择
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_label = QLabel("选择日期：")
        self.date_picker = QDateEdit()
        self.date_picker.setMinimumWidth(120)  # 设置最小宽度
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("yyyy-MM-dd")  # 设置日期显示格式
        
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_picker)
        
        # 时间范围选择
        range_widget = QWidget()
        range_layout = QHBoxLayout(range_widget)
        range_layout.setContentsMargins(0, 0, 0, 0)
        
        self.range_label = QLabel("时间范围：")
        self.range_combo = QComboBox()
        self.range_combo.setMinimumWidth(100)  # 设置最小宽度
        self.range_combo.addItems(["今天", "最近7天", "最近30天", "全部"])
        
        range_layout.addWidget(self.range_label)
        range_layout.addWidget(self.range_combo)
        
        # 在筛选区域添加批量操作按钮
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.batch_delete_btn.setEnabled(False)  # 初始时禁用
        self.batch_delete_btn.clicked.connect(self.batch_delete_records)
        
        # 添加到筛选布局
        filter_layout.addWidget(date_widget)
        filter_layout.addWidget(range_widget)
        filter_layout.addWidget(self.batch_delete_btn)
        filter_layout.addStretch()  # 添加弹性空间
        
        # 添加到主布局
        layout.addWidget(filter_group)
        layout.addWidget(self.table)
        
        # 连接信号
        self.date_picker.dateChanged.connect(self.update_table)
        self.range_combo.currentTextChanged.connect(self.update_table)
        
        # 添加右键菜单功能
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # 添加双击编辑功能
        self.table.cellDoubleClicked.connect(self.handle_double_click)
        
        # 初始化显示
        self.update_table()

    def setup_table_properties(self):
        """设置表格属性"""
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f8f8;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: none;
                border-right: 1px solid #d0d0d0;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 日期
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # 时间
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # 食物名称
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 重量
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 卡路里

    def update_table(self):
        """更新表格数据"""
        self.table.setRowCount(0)  # 清空现有数据
        
        # 根据选择的时间范围获取数据
        range_text = self.range_combo.currentText()
        if range_text == "今天":
            start_date = datetime.now().date()
        elif range_text == "最近7天":
            start_date = datetime.now().date() - timedelta(days=7)
        elif range_text == "最近30天":
            start_date = datetime.now().date() - timedelta(days=30)
        else:  # 全部
            start_date = None
            
        # 从数据库获取记录
        records = self.db_manager.get_records_by_date_range(start_date)
        
        # 填充表格
        for row, record in enumerate(records):
            self.table.insertRow(row)
            
            # 获取记录详情
            details = self.db_manager.get_record_details(record[0])
            if not details:
                continue
                
            try:
                # 解析时间戳
                timestamp = datetime.strptime(details['record'][5], '%Y-%m-%d %H:%M:%S.%f')
                
                # 设置日期和时间，并保存记录ID
                date_item = QTableWidgetItem(timestamp.strftime('%Y-%m-%d'))
                date_item.setData(Qt.ItemDataRole.UserRole, record[0])  # 保存记录ID
                self.table.setItem(row, 0, date_item)
                self.table.setItem(row, 1, QTableWidgetItem(timestamp.strftime('%H:%M:%S')))
                
                # 解析JSON数据
                raw_data = json.loads(details['record'][6])
                
                # 获取第一个食物的信息
                if raw_data.get('foods'):
                    food = raw_data['foods'][0]
                    self.table.setItem(row, 2, QTableWidgetItem(food.get('name', '未知')))
                    self.table.setItem(row, 3, QTableWidgetItem(str(food.get('weight', 0))))
                    self.table.setItem(row, 4, QTableWidgetItem(str(food.get('calories', 0))))
                
            except Exception as e:
                print(f"处理记录时出错: {str(e)}")
                continue

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        
        # 获取选中的行数
        selected_rows = len(self.table.selectedItems()) // self.table.columnCount()
        
        if selected_rows == 1:
            # 单选时显示编辑和删除选项
            edit_action = menu.addAction("编辑")
            delete_action = menu.addAction("删除")
        elif selected_rows > 1:
            # 多选时只显示删除选项
            edit_action = None
            delete_action = menu.addAction(f"删除选中的 {selected_rows} 条记录")
        else:
            return
            
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action:
            if selected_rows == 1:
                row = self.table.rowAt(position.y())
                if action == edit_action:
                    self.edit_record(row)
                elif action == delete_action:
                    self.delete_record(row)
            elif action == delete_action:
                self.batch_delete_records()

    def handle_double_click(self, row, column):
        """处理双击事件"""
        self.edit_record(row)

    def edit_record(self, row):
        """编辑记录"""
        # 获取记录ID
        record_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 创建编辑对话框
        dialog = EditFoodDialog(self.db_manager, record_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 获取更新后的数据
            updated_data = dialog.get_updated_data()
            
            # 更新数据库
            if self.db_manager.update_record(record_id, updated_data):
                self.update_table()  # 刷新表格
                QMessageBox.information(self, "成功", "记录已更新")
            else:
                QMessageBox.critical(self, "错误", "更新记录失败")

    def delete_record(self, row):
        """删除记录"""
        # 获取记录ID
        record_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 显示确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除记录
            if self.db_manager.delete_record(record_id):
                self.update_table()  # 刷新表格
                QMessageBox.information(self, "成功", "记录已删除")
            else:
                QMessageBox.critical(self, "错误", "删除记录失败")

    def update_batch_delete_button(self):
        """更新批量删除按钮状态"""
        selected_rows = len(self.table.selectedItems()) // self.table.columnCount()
        self.batch_delete_btn.setEnabled(selected_rows > 0)
        if selected_rows > 0:
            self.batch_delete_btn.setText(f"批量删除 ({selected_rows})")
        else:
            self.batch_delete_btn.setText("批量删除")

    def batch_delete_records(self):
        """批量删除记录"""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            return
            
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认批量删除",
            f"确定要删除选中的 {len(selected_rows)} 条记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 收集所有要删除的记录ID
            record_ids = []
            for row in selected_rows:
                record_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                record_ids.append(record_id)
            
            # 创建进度对话框
            progress = QProgressDialog("正在删除记录...", "取消", 0, len(record_ids), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            
            # 执行删除操作
            success_count = 0
            for i, record_id in enumerate(record_ids):
                if progress.wasCanceled():
                    break
                    
                if self.db_manager.delete_record(record_id):
                    success_count += 1
                    
                progress.setValue(i + 1)
            
            # 显示结果
            if success_count > 0:
                QMessageBox.information(
                    self,
                    "完成",
                    f"批量删除完成\n成功删除: {success_count}/{len(record_ids)} 条记录"
                )
                self.update_table()  # 刷新表格
            else:
                QMessageBox.critical(self, "错误", "删除记录失败")
            
            progress.close()

class EditFoodDialog(QDialog):
    """食物记录编辑对话框"""
    def __init__(self, db_manager, record_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_id = record_id
        self.record_data = None
        self.init_ui()
        self.load_record()
        
    def init_ui(self):
        self.setWindowTitle("编辑记录")
        self.setMinimumWidth(1200)  # 增加窗口宽度
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # 增加组件间距
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 餐点类型选择
        self.meal_type = QComboBox()
        self.meal_type.addItems(["早餐", "午餐", "晚餐", "小食"])
        form_layout.addRow("餐点类型:", self.meal_type)
        
        # 健康建议
        self.health_tips = QLineEdit()
        self.health_tips.setMinimumWidth(400)  # 设置最小宽度
        form_layout.addRow("健康建议:", self.health_tips)
        
        # 创建食物列表区域
        self.foods_group = QGroupBox("食物列表")
        self.foods_layout = QVBoxLayout()
        self.foods_layout.setSpacing(10)
        self.foods_group.setLayout(self.foods_layout)
        
        # 添加食物按钮
        self.add_food_btn = QPushButton("添加食物")
        self.add_food_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_food_btn.clicked.connect(self.add_food_item)
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加到主布局
        layout.addLayout(form_layout)
        layout.addWidget(self.foods_group)
        layout.addWidget(self.add_food_btn)
        layout.addWidget(button_box)
        
    def add_food_item(self, food_data=None):
        """添加食物输入组件"""
        food_widget = QWidget()
        food_layout = QHBoxLayout(food_widget)
        food_layout.setContentsMargins(5, 5, 5, 5)
        food_layout.setSpacing(10)  # 增加组件间距
        
        # 食物名称
        name = QLineEdit()
        name.setPlaceholderText("食物名称")
        name.setMinimumWidth(200)  # 增加名称输入框宽度
        
        # 创建数值输入框
        def create_spinbox(suffix, prefix="", max_value=1000, decimals=2):
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, max_value)
            spinbox.setDecimals(decimals)
            spinbox.setSuffix(suffix)
            spinbox.setPrefix(prefix)
            spinbox.setMinimumWidth(150)  # 增加宽度以适应更长的数字
            spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)  # 右对齐数字
            # 使用默认的上下按钮，但调整样式
            spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    padding-right: 15px;  /* 为按钮留出空间 */
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 15px;
                }
            """)
            spinbox.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
            spinbox.setSingleStep(1)
            return spinbox
        
        # 创建各个输入框
        weight = create_spinbox("g", max_value=2000)
        calories = create_spinbox("kcal", max_value=2000)
        protein = create_spinbox("g", "蛋白质:", max_value=200)
        fat = create_spinbox("g", "脂肪:", max_value=200)
        carbs = create_spinbox("g", "碳水:", max_value=200)
        fiber = create_spinbox("g", "纤维:", max_value=50)
        sodium = create_spinbox("mg", "钠:", max_value=5000, decimals=0)
        
        # 如果有现有数据，设置值
        if food_data:
            name.setText(food_data.get('name', ''))
            weight.setValue(float(food_data.get('weight', 0)))
            calories.setValue(float(food_data.get('calories', 0)))
            
            nutrition = food_data.get('nutrition', {})
            protein.setValue(float(nutrition.get('protein', 0)))
            fat.setValue(float(nutrition.get('fat', 0)))
            carbs.setValue(float(nutrition.get('carbohydrates', 0)))
            fiber.setValue(float(nutrition.get('fiber', 0)))
            sodium.setValue(float(nutrition.get('sodium', 0)))
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_food_item(food_widget))
        
        # 直接添加所有组件到布局
        food_layout.addWidget(name)
        food_layout.addWidget(weight)
        food_layout.addWidget(calories)
        food_layout.addWidget(protein)
        food_layout.addWidget(fat)
        food_layout.addWidget(carbs)
        food_layout.addWidget(fiber)
        food_layout.addWidget(sodium)
        food_layout.addWidget(delete_btn)
        
        # 设置组件的对象名
        name.setObjectName("name")
        weight.setObjectName("weight")
        calories.setObjectName("calories")
        protein.setObjectName("protein")
        fat.setObjectName("fat")
        carbs.setObjectName("carbs")
        fiber.setObjectName("fiber")
        sodium.setObjectName("sodium")
        
        self.foods_layout.addWidget(food_widget)
        return food_widget
        
    def remove_food_item(self, widget):
        """删除食物输入组件"""
        widget.deleteLater()
        
    def load_record(self):
        """加载记录数据"""
        details = self.db_manager.get_record_details(self.record_id)
        if not details:
            return
            
        try:
            self.record_data = json.loads(details['record'][6])  # raw_json
            
            # 设置餐点类型
            meal_type = self.record_data.get('meal_category', '未知')
            index = self.meal_type.findText(meal_type)
            if index >= 0:
                self.meal_type.setCurrentIndex(index)
            
            # 设置食物列表
            for food in self.record_data.get('foods', []):
                self.add_food_item(food)
            
            # 设置健康建议
            self.health_tips.setText(self.record_data.get('health_tips', ''))
            
        except Exception as e:
            print(f"加载记录数据失败: {str(e)}")
            
    def get_updated_data(self):
        """获取更新后的数据"""
        foods = []
        total_calories = 0
        
        # 收集所有食物数据
        for i in range(self.foods_layout.count()):
            widget = self.foods_layout.itemAt(i).widget()
            if widget:
                layout = widget.layout()
                name = layout.itemAt(0).widget().text()
                weight = layout.itemAt(1).widget().value()
                calories = layout.itemAt(2).widget().value()
                protein = layout.itemAt(3).widget().value()
                fat = layout.itemAt(4).widget().value()
                carbs = layout.itemAt(5).widget().value()
                fiber = layout.itemAt(6).widget().value()
                sodium = layout.itemAt(7).widget().value()
                
                if name:  # 只添加有名称的食物
                    food_data = {
                        'name': name,
                        'weight': weight,
                        'calories': calories,
                        'category': '未分类',
                        'nutrition': {
                            'protein': protein,
                            'fat': fat,
                            'carbohydrates': carbs,
                            'fiber': fiber,
                            'sodium': sodium
                        }
                    }
                    foods.append(food_data)
                    total_calories += calories
        
        return {
            'foods': foods,
            'total_calories': total_calories,
            'meal_category': self.meal_type.currentText(),
            'health_tips': self.health_tips.text()
        }

class DailyStatisticsDialog(QDialog):
    """每日摄入统计对话框"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        # 设置图表字体
        self.font = {'family': 'Microsoft YaHei',
                    'weight': 'normal',
                    'size': 9}
        matplotlib.rc('font', **self.font)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("每日摄入统计")
        self.setMinimumSize(900, 600)  # 增加窗口大小以适应图表
        
        layout = QVBoxLayout(self)
        
        # 部控制区域
        top_layout = QHBoxLayout()
        
        # 日期选择
        date_layout = QHBoxLayout()
        self.date_label = QLabel("选择日期：")
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_picker)
        
        # 图表类型选择
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            "营养成分分布",
            "餐点卡路里分布",
            "一周卡路里趋势",
            "一周营养成分趋势"
        ])
        
        top_layout.addLayout(date_layout)
        top_layout.addWidget(QLabel("图表类型："))
        top_layout.addWidget(self.chart_type)
        top_layout.addStretch()
        
        # 创建分割布局
        split_layout = QHBoxLayout()
        
        # 左侧统计信息
        self.stats_text = QLabel()
        self.stats_text.setWordWrap(True)
        self.stats_text.setStyleSheet("""
            QLabel {
                background-color: white;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                min-width: 300px;
            }
        """)
        
        # 右侧图表区域
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        
        split_layout.addWidget(self.stats_text)
        split_layout.addWidget(self.canvas)
        
        # 添加到主布局
        layout.addLayout(top_layout)
        layout.addLayout(split_layout)
        
        # 连接信号
        self.date_picker.dateChanged.connect(self.update_statistics)
        self.chart_type.currentTextChanged.connect(self.update_chart)
        
        # 初始化显示
        self.update_statistics()
        
    def update_statistics(self):
        """更新统计信息"""
        selected_date = self.date_picker.date().toPyDate()
        stats = self.db_manager.get_daily_statistics(selected_date)
        
        if not stats:
            self.stats_text.setText("没有找到统计数据")
            return
            
        # 格式化统计���息
        text = []
        text.append(f"<h2>每日摄入统计 ({stats['date']})</h2>")
        text.append(f"<h3>总卡路里: {stats['total_calories']:.1f} kcal</h3>")
        
        # 营养成分汇总
        text.append("<h3>营养成分汇总:</h3>")
        nutrition = stats['nutrition']
        text.append("<table style='margin-left: 20px'>")
        text.append(f"<tr><td>蛋白质:</td><td>{nutrition['protein']:.1f}g</td></tr>")
        text.append(f"<tr><td>脂肪:</td><td>{nutrition['fat']:.1f}g</td></tr>")
        text.append(f"<tr><td>碳水化合物:</td><td>{nutrition['carbohydrates']:.1f}g</td></tr>")
        text.append(f"<tr><td>膳食纤维:</td><td>{nutrition['fiber']:.1f}g</td></tr>")
        text.append(f"<tr><td>钠:</td><td>{nutrition['sodium']:.1f}mg</td></tr>")
        text.append("</table>")
        
        # 各点详情
        text.append("<h3>餐点详情:</h3>")
        for meal_type, meal_data in stats['meals'].items():
            text.append(f"<div style='margin-left: 20px'>")
            text.append(f"<h4>{meal_type}</h4>")
            text.append(f"<p>总卡路里: {meal_data['calories']:.1f} kcal</p>")
            text.append(f"<p>记录数: {meal_data['count']}</p>")
            if meal_data['foods']:
                text.append("<p>食物列表:</p>")
                text.append("<ul>")
                for food in meal_data['foods']:
                    text.append(
                        f"<li>{food['name']}: {food['weight']}g, "
                        f"{food['calories']}kcal</li>"
                    )
                text.append("</ul>")
            text.append("</div>")
        
        self.stats_text.setText("".join(text))
        self.update_chart()
        
    def update_chart(self):
        """更新图表显示"""
        selected_date = self.date_picker.date().toPyDate()
        chart_type = self.chart_type.currentText()
        
        # 清除现图表
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if chart_type == "营养成分分布":
            self.plot_nutrition_distribution(ax, selected_date)
        elif chart_type == "餐点卡路里分布":
            self.plot_meal_distribution(ax, selected_date)
        elif chart_type == "一周卡路里趋势":
            self.plot_weekly_calories(ax, selected_date)
        elif chart_type == "一周营养成分趋势":
            self.plot_weekly_nutrition(ax, selected_date)
            
        self.canvas.draw()
        
    def plot_nutrition_distribution(self, ax, date):
        """绘制营养成分分布饼图"""
        stats = self.db_manager.get_daily_statistics(date)
        if not stats:
            return
            
        nutrition = stats['nutrition']
        labels = ['蛋白质', '脂肪', '碳水化合物', '膳食纤维']
        sizes = [
            nutrition['protein'],
            nutrition['fat'],
            nutrition['carbohydrates'],
            nutrition['fiber']
        ]
        
        # 设置饼图文字性
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
               textprops={'fontsize': 9, 'fontfamily': 'Microsoft YaHei'})
        ax.set_title(f"营养成分分布 ({date})", fontsize=10, pad=10)
        
    def plot_meal_distribution(self, ax, date):
        """绘制餐点卡路里分布柱状图"""
        stats = self.db_manager.get_daily_statistics(date)
        if not stats:
            return
            
        meals = stats['meals']
        names = list(meals.keys())
        values = [meal['calories'] for meal in meals.values()]
        
        ax.bar(names, values)
        ax.set_title(f"餐点卡路里分布 ({date})", fontsize=10, pad=10)
        ax.set_ylabel('卡路里 (kcal)', fontsize=9)
        ax.tick_params(axis='both', labelsize=8)
        
    def plot_weekly_calories(self, ax, end_date):
        """绘制一周卡路里趋势线图"""
        dates = []
        calories = []
        
        # 获取过去7天的数据
        for i in range(6, -1, -1):
            date = end_date - timedelta(days=i)
            stats = self.db_manager.get_daily_statistics(date)
            dates.append(date.strftime('%m-%d'))
            calories.append(stats['total_calories'] if stats else 0)
        
        ax.plot(dates, calories, marker='o')
        ax.set_title("一周卡路里趋势", fontsize=10, pad=10)
        ax.set_xlabel('日期', fontsize=9)
        ax.set_ylabel('卡路里 (kcal)', fontsize=9)
        ax.tick_params(axis='both', labelsize=8)
        ax.tick_params(axis='x', rotation=45)
        
    def plot_weekly_nutrition(self, ax, end_date):
        """绘制一周营养成分趋势线图"""
        dates = []
        protein = []
        fat = []
        carbs = []
        
        # 获取过去7天的数据
        for i in range(6, -1, -1):
            date = end_date - timedelta(days=i)
            stats = self.db_manager.get_daily_statistics(date)
            dates.append(date.strftime('%m-%d'))
            if stats:
                protein.append(stats['nutrition']['protein'])
                fat.append(stats['nutrition']['fat'])
                carbs.append(stats['nutrition']['carbohydrates'])
            else:
                protein.append(0)
                fat.append(0)
                carbs.append(0)
        
        ax.plot(dates, protein, marker='o', label='蛋白质')
        ax.plot(dates, fat, marker='s', label='脂肪')
        ax.plot(dates, carbs, marker='^', label='碳水化合物')
        ax.set_title("一周营养成分趋势", fontsize=10, pad=10)
        ax.set_xlabel('日期', fontsize=9)
        ax.set_ylabel('克 (g)', fontsize=9)
        ax.tick_params(axis='both', labelsize=8)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(prop={'size': 8})

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
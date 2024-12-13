# Food Calorie Detection

一个简单的食物卡路里检测和记录应用。

## 功能特点

- 上传食物图片进行分析
- 识别食物类型和估算卡路里
- 记录每日饮食数据
- 查看历史记录和统计数据

## 开发计划

### 1. 基础界面搭建
- [x] 主窗口设计
  - [x] 图片上传按钮
  - [x] 图片预览区域
  - [x] 分析结果显示区域
  - [x] 历史记录查看按钮

### 2. 图片处理功能
- [x] 图片上传功能
  - [x] 文件选择对话框
  - [x] 图片预览功能
  - [x] 图片保存到images目录

### 3. 数据库功能
- [ ] 数据库设计
  - [ ] 创建食物记录表
  - [ ] 创建每日记录表
- [ ] 基本数据操作
  - [ ] 添加记录
  - [ ] 查询记录
  - [ ] 修改记录
  - [ ] 删除记录

### 4. AI识别功能
- [x] 接入AI API
  - [x] 图片分析
  - [x] 结果解析
  - [ ] 数据存储

### 5. 数据展示
- [ ] 历史记录列表
- [ ] 每日摄入统计
- [ ] 简单数据可视化

## 安装说明

1. 克隆项目到本地
2. 创建虚拟环境（推荐）：   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows   ```
3. 安装依赖：   ```bash
   pip install -r requirements.txt   ```

## 使用说明

运行主程序：
```bash
python main.py
``` 


import sqlite3
import json
from datetime import datetime
import os
import re

class DatabaseManager:
    def __init__(self, db_name="food_records.db"):
        """初始化数据库管理器"""
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # 创建食物记录主表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT,
                    meal_category TEXT,
                    total_calories REAL,
                    health_tips TEXT,
                    record_date DATETIME,
                    raw_json TEXT
                )
            ''')
            
            # 创建食物详情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id INTEGER,
                    food_name TEXT,
                    category TEXT,
                    weight REAL,
                    calories REAL,
                    FOREIGN KEY (record_id) REFERENCES food_records (id)
                )
            ''')
            
            # 创建营养成分表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nutrition_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_detail_id INTEGER,
                    protein REAL,
                    fat REAL,
                    carbohydrates REAL,
                    fiber REAL,
                    sodium REAL,
                    FOREIGN KEY (food_detail_id) REFERENCES food_details (id)
                )
            ''')
            
            conn.commit()

    def extract_json_from_response(self, response_text):
        """从API响应中提取JSON数据"""
        try:
            # 首先尝试直接解析
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                pass

            # 尝试从代码块中提取JSON
            json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            matches = re.findall(json_pattern, response_text)
            
            if matches:
                # 使用找到的第一个匹配项
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError as e:
                    print(f"提取的JSON解析失败: {e}")
                    raise

            # 如果没有代码块标记，尝试直接查找JSON对象
            json_object_pattern = r'(\{[\s\S]*\})'
            matches = re.findall(json_object_pattern, response_text)
            
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError as e:
                    print(f"提取的JSON对象解析失败: {e}")
                    raise

            raise ValueError("无法从响应中提取有效的JSON数据")

        except Exception as e:
            print(f"JSON提取失败: {str(e)}")
            print(f"原始响应: {response_text}")
            raise

    def save_analysis_result(self, image_path, analysis_result):
        """保存分析结果到数据库"""
        try:
            # 解析JSON数据
            if isinstance(analysis_result, str):
                # 从响应中提取JSON数据
                data = self.extract_json_from_response(analysis_result)
            else:
                data = analysis_result

            print("成功解析JSON数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 保存主记录
                cursor.execute('''
                    INSERT INTO food_records 
                    (image_path, meal_category, total_calories, health_tips, record_date, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    image_path,
                    data.get('meal_category'),
                    float(data.get('total_calories', 0)),
                    data.get('health_tips'),
                    datetime.now(),
                    json.dumps(data)
                ))
                
                record_id = cursor.lastrowid
                
                # 保存食物详情
                for food in data.get('foods', []):
                    cursor.execute('''
                        INSERT INTO food_details 
                        (record_id, food_name, category, weight, calories)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        record_id,
                        food.get('name'),
                        food.get('category'),
                        float(food.get('weight', 0)),
                        float(food.get('calories', 0))
                    ))
                    
                    food_detail_id = cursor.lastrowid
                    
                    # 保存营养信息
                    nutrition = food.get('nutrition', {})
                    cursor.execute('''
                        INSERT INTO nutrition_info 
                        (food_detail_id, protein, fat, carbohydrates, fiber, sodium)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        food_detail_id,
                        float(nutrition.get('protein', 0)),
                        float(nutrition.get('fat', 0)),
                        float(nutrition.get('carbohydrates', 0)),
                        float(nutrition.get('fiber', 0)),
                        float(nutrition.get('sodium', 0))
                    ))
                
                conn.commit()
                print(f"数据保存成功，记录ID: {record_id}")
                return record_id
                
        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            raise

    def get_daily_records(self, date=None):
        """获取指定日期的所有记录"""
        if date is None:
            date = datetime.now().date()
            
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM food_records 
                WHERE date(record_date) = date(?)
            ''', (date,))
            return cursor.fetchall()

    def get_record_details(self, record_id):
        """获取特定记录的详细信息"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # 获取主记录
            cursor.execute('SELECT * FROM food_records WHERE id = ?', (record_id,))
            record = cursor.fetchone()
            
            if not record:
                return None
                
            # 获取食物详情
            cursor.execute('SELECT * FROM food_details WHERE record_id = ?', (record_id,))
            food_details = cursor.fetchall()
            
            # 获取每个食物的营养信息
            result = {
                'record': record,
                'foods': []
            }
            
            for food in food_details:
                cursor.execute('SELECT * FROM nutrition_info WHERE food_detail_id = ?', (food[0],))
                nutrition = cursor.fetchone()
                result['foods'].append({
                    'food': food,
                    'nutrition': nutrition
                })
                
            return result 
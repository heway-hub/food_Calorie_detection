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
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError as e:
                    print(f"提取的JSON解析失败: {e}")
                    print(f"提取的内容: {matches[0]}")
                    raise

            # 如果没有代码块标记，尝试直接查找JSON对象
            json_object_pattern = r'(\{[\s\S]*\})'
            matches = re.findall(json_object_pattern, response_text)
            
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError as e:
                    print(f"提取的JSON对象解析失败: {e}")
                    print(f"提取的内容: {matches[0]}")
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
                data = self.extract_json_from_response(analysis_result)
            else:
                data = analysis_result

            # 验证必��数据字段
            if not isinstance(data, dict):
                raise ValueError("分析结果必须是一个字典")
            
            if 'foods' not in data:
                raise ValueError("分析结果缺少foods字段")
            
            if not isinstance(data.get('foods'), list):
                raise ValueError("foods必须是一个列表")

            # 检查是否已存在相同的记录
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 检查是否存在相同时间、相同餐点类型的记录
                cursor.execute('''
                    SELECT id FROM food_records 
                    WHERE date(record_date) = date(?) 
                    AND meal_category = ?
                    AND image_path = ?
                ''', (
                    datetime.now(),
                    data.get('meal_category', '未分类'),
                    image_path
                ))
                
                existing_record = cursor.fetchone()
                if existing_record:
                    print(f"记录已存在，记录ID: {existing_record[0]}")
                    return existing_record[0]

                try:
                    # 保存主记录
                    cursor.execute('''
                        INSERT INTO food_records 
                        (image_path, meal_category, total_calories, health_tips, record_date, raw_json)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        image_path,
                        data.get('meal_category', '未分类'),
                        float(data.get('total_calories', 0)),
                        data.get('health_tips', ''),
                        datetime.now(),
                        json.dumps(data, ensure_ascii=False)
                    ))
                    
                    record_id = cursor.lastrowid
                    
                    # 保存食物详情
                    for food in data.get('foods', []):
                        try:
                            cursor.execute('''
                                INSERT INTO food_details 
                                (record_id, food_name, category, weight, calories)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                record_id,
                                food.get('name', '未知食物'),
                                food.get('category', '未分类'),
                                float(food.get('weight', 0)),
                                float(food.get('calories', 0))
                            ))
                        except Exception as e:
                            print(f"保存食物详情失败: {str(e)}")
                            print(f"问题数据: {food}")
                            continue
                    
                    conn.commit()
                    print(f"数据保存成功，记录ID: {record_id}")
                    return record_id
                    
                except sqlite3.Error as e:
                    print(f"数据库操作失败: {str(e)}")
                    conn.rollback()
                    raise

        except Exception as e:
            print(f"保存数据失败: {str(e)}")
            print(f"原始数据: {analysis_result}")
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
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 获取主记录
                cursor.execute('SELECT * FROM food_records WHERE id = ?', (record_id,))
                record = cursor.fetchone()
                
                if not record:
                    return None
                
                # 从raw_json中获取完整数据
                try:
                    raw_data = json.loads(record[6])  # raw_json字段
                    
                    # 构建结果
                    result = {
                        'record': record,
                        'foods': []
                    }
                    
                    # 从raw_json中获取食物详情（包含完整的营养信息）
                    for food in raw_data.get('foods', []):
                        food_info = {
                            'food': (
                                None,  # food_detail_id (不需要)
                                record_id,
                                food.get('name', ''),
                                food.get('category', ''),
                                food.get('weight', 0),
                                food.get('calories', 0)
                            ),
                            'nutrition': food.get('nutrition', {})
                        }
                        result['foods'].append(food_info)
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    return None
                
        except Exception as e:
            print(f"获取记录详情失败: {str(e)}")
            return None

    def get_records_by_date_range(self, start_date=None):
        """获取指定日期范围内的所有记录"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            if start_date:
                cursor.execute('''
                    SELECT * FROM food_records 
                    WHERE date(record_date) >= date(?)
                    ORDER BY record_date DESC
                ''', (start_date,))
            else:
                cursor.execute('''
                    SELECT * FROM food_records 
                    ORDER BY record_date DESC
                ''')
                
            return cursor.fetchall()

    def update_record(self, record_id, updated_data):
        """更新记录"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 更新主记录
                cursor.execute('''
                    UPDATE food_records 
                    SET meal_category = ?, 
                        total_calories = ?,
                        health_tips = ?,
                        raw_json = ?
                    WHERE id = ?
                ''', (
                    updated_data.get('meal_category'),
                    float(updated_data.get('total_calories', 0)),
                    updated_data.get('health_tips'),
                    json.dumps(updated_data),
                    record_id
                ))
                
                # 删除旧的食物详情和营养信息
                cursor.execute('DELETE FROM nutrition_info WHERE food_detail_id IN (SELECT id FROM food_details WHERE record_id = ?)', (record_id,))
                cursor.execute('DELETE FROM food_details WHERE record_id = ?', (record_id,))
                
                # 添加新的食物详情
                for food in updated_data.get('foods', []):
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
                    
                    # 添加营养信息
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
                return True
                
        except Exception as e:
            print(f"更新记录失败: {str(e)}")
            return False

    def delete_record(self, record_id):
        """删除记录及其相关数据"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 首先获取记录信息（用于删除图片）
                cursor.execute('SELECT image_path FROM food_records WHERE id = ?', (record_id,))
                record = cursor.fetchone()
                
                if record and record[0]:
                    # 删除图片文件
                    image_path = record[0]
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"删除图片文件失败: {str(e)}")
                
                # 删除营养信息
                cursor.execute('''
                    DELETE FROM nutrition_info 
                    WHERE food_detail_id IN (
                        SELECT id FROM food_details WHERE record_id = ?
                    )
                ''', (record_id,))
                
                # 删除食物详情
                cursor.execute('DELETE FROM food_details WHERE record_id = ?', (record_id,))
                
                # 删除主记录
                cursor.execute('DELETE FROM food_records WHERE id = ?', (record_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"删除记录失败: {str(e)}")
            return False

    def get_daily_statistics(self, date=None):
        """获取每日摄入统计数据"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                if date is None:
                    date = datetime.now().date()
                
                # 获取指定日期的所有记录，按meal_category分组
                cursor.execute('''
                    SELECT raw_json
                    FROM food_records 
                    WHERE date(record_date) = date(?)
                    GROUP BY meal_category
                ''', (date,))
                
                records = cursor.fetchall()
                
                # 初始化统计数据
                stats = {
                    'date': date.strftime('%Y-%m-%d') if isinstance(date, datetime) else date,
                    'total_calories': 0,
                    'meals': {},
                    'nutrition': {
                        'protein': 0,
                        'fat': 0,
                        'carbohydrates': 0,
                        'fiber': 0,
                        'sodium': 0
                    }
                }
                
                # 处理每条记录
                processed_foods = set()  # 用于去重
                for record in records:
                    try:
                        data = json.loads(record[0])  # raw_json
                        meal_category = data.get('meal_category', '其他')
                        
                        # 初始化餐点数据（如果不存在）
                        if meal_category not in stats['meals']:
                            stats['meals'][meal_category] = {
                                'calories': 0,
                                'count': 0,
                                'foods': []
                            }
                        
                        # 更新餐点统计
                        stats['meals'][meal_category]['count'] += 1
                        
                        # 处理食物数据
                        for food in data.get('foods', []):
                            # 创建食物唯一标识
                            food_key = f"{meal_category}_{food.get('name')}_{food.get('weight')}"
                            if food_key in processed_foods:
                                continue
                            processed_foods.add(food_key)
                            
                            # 更新总卡路里
                            calories = float(food.get('calories', 0))
                            stats['total_calories'] += calories
                            stats['meals'][meal_category]['calories'] += calories
                            
                            # 添加食物到餐点列表
                            stats['meals'][meal_category]['foods'].append({
                                'name': food.get('name'),
                                'calories': calories,
                                'weight': food.get('weight', 0)
                            })
                            
                            # 更新营养成分
                            nutrition = food.get('nutrition', {})
                            stats['nutrition']['protein'] += float(nutrition.get('protein', 0))
                            stats['nutrition']['fat'] += float(nutrition.get('fat', 0))
                            stats['nutrition']['carbohydrates'] += float(nutrition.get('carbohydrates', 0))
                            stats['nutrition']['fiber'] += float(nutrition.get('fiber', 0))
                            stats['nutrition']['sodium'] += float(nutrition.get('sodium', 0))
                            
                    except Exception as e:
                        print(f"处理记录时出错: {str(e)}")
                        continue
                
                return stats
                
        except Exception as e:
            print(f"获取每日统计数据失败: {str(e)}")
            return None

    def get_all_records(self):
        """获取所有食物记录"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # 从数据库获取所有记录
                query = """
                    SELECT id, record_date, raw_json, meal_category
                    FROM food_records
                    ORDER BY record_date DESC
                """
                cursor.execute(query)
                records = cursor.fetchall()
                
                # 格式化记录
                formatted_records = []
                for record in records:
                    record_id, timestamp, raw_json, meal_category = record
                    try:
                        # 解析JSON数据
                        food_data = json.loads(raw_json)
                        formatted_records.append({
                            'id': record_id,
                            'timestamp': timestamp,
                            'foods': food_data.get('foods', []),
                            'total_calories': food_data.get('total_calories', 0),
                            'meal_category': meal_category
                        })
                    except json.JSONDecodeError:
                        print(f"解析记录 {record_id} 的JSON数据失败")
                        continue
                
                return formatted_records
                
        except Exception as e:
            print(f"获取记录失败: {str(e)}")
            return []
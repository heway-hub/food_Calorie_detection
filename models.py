import os
import base64
from openai import OpenAI
from PyQt6.QtCore import QThread, pyqtSignal
import json
import re

class AIAnalyzer(QThread):
    """处理AI分析的线程类"""
    analysis_complete = pyqtSignal(str)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.api_key = "sk-wYL74sSimSWv1N6UCb7780CcF55242Dc90Eb34A395A4E602"
        self.base_url = "https://api.tu-zi.com/v1"
    
    def encode_image(self):
        """将图片转换为base64编码，并添加调试信息"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.image_path):
                raise FileNotFoundError(f"图片文件不存在: {self.image_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(self.image_path)
            print(f"图片文件大小: {file_size} bytes")
            
            # 读取并编码图片
            with open(self.image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                
                # 打印编码后的前100个字符（用于调试）
                print(f"Base64编码预览 (前100字符): {base64_data[:100]}")
                print(f"Base64编码总长: {len(base64_data)}")
                
                return base64_data
                
        except Exception as e:
            raise Exception(f"图片编码失败: {str(e)}")
        
    def run(self):
        """执行AI分析"""
        try:
            print(f"\n开始分析图片: {self.image_path}")
            
            # 编码图片
            base64_image = self.encode_image()
            
            # 初始化OpenAI客户端
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 准备请求数据
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的食物营养分析师。你必须严格按照以下JSON格式输出分析结果，不要包含任何其他文本或解释。
输出必须是可以直接被json.loads()解析的标准JSON格式：

{
    "foods": [
        {
            "name": "食物名称",
            "category": "食物类别(主食/肉类/蔬菜/调味品等)",
            "weight": "估算重量(克)",
            "calories": "卡路里",
            "components": [
                {
                    "name": "组成部分名称",
                    "weight": "重量(克)",
                    "category": "成分类别",
                    "calories": "该部分卡路里"
                }
            ],
            "nutrition": {
                "protein": "蛋白质(克)",
                "fat": "脂肪(克)",
                "carbohydrates": "碳水化合物(克)",
                "fiber": "膳食纤维(克)",
                "sodium": "钠(毫克)"
            }
        }
    ],
    "total_calories": "总卡路里",
    "meal_category": "餐点类型(早餐/午餐/晚餐/小食)",
    "health_tips": "健康建议"
}

注意：
1. 所有数值必须是数字而不是字符串
2. 不要输出任何额外的文本说明
3. 确保输出是标准的JSON格式
4. 不要包含任何注释或markdown标记"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "分析这张食物图片，识别所有食物及其组成部分，估算重量和卡路里，分析营养成分。必须严格按照系统提示的JSON格式输出，不要包含任何其他文本。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            print("发送API请求...")
            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # 提取分析结果
            result = response.choices[0].message.content
            print("收到API响应:")
            print("-" * 50)
            print(result)
            print("-" * 50)
            
            # 验证JSON格式
            try:
                # 尝试从代码块中提取JSON
                json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
                matches = re.findall(json_pattern, result)
                
                if matches:
                    # 使用找到的第一个匹配项
                    json_str = matches[0]
                else:
                    # 如果没有代码块标记，使用原始响应
                    json_str = result
                
                # 解析JSON
                json_result = json.loads(json_str)
                
                # 基本验证
                if not isinstance(json_result, dict) or 'foods' not in json_result:
                    raise ValueError("返回的JSON格式不正确")
                
                # 发送解析后的JSON字符串
                self.analysis_complete.emit(json.dumps(json_result))
                    
            except Exception as e:
                raise ValueError(f"JSON处理失败: {str(e)}")
            
        except Exception as e:
            error_msg = f"分析过程出错: {str(e)}"
            print(f"错误详情: {error_msg}")
            self.analysis_error.emit(error_msg)
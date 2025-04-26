import json
import csv
import os
import datetime
from pathlib import Path

def save_to_csv(json_str_result, source, credible, file_path=None):
    """
    将JSON数据和额外信息保存到CSV文件中，JSON中的每条数据作为单独的一行
    
    参数:
        json_str_result (str): JSON格式的字符串数据
        source (str): 来源信息
        credible (str): 可信度信息
        file_path (str, 可选): 指定的文件路径，若不提供则使用默认路径
    """
    # 解析JSON数据
    try:
        data = json.loads(json_str_result)
    except json.JSONDecodeError:
        print("JSON数据解析失败")
        return
    
    # 检查JSON数据结构
    if 'news' not in data or not isinstance(data['news'], list):
        print("JSON数据格式不正确，缺少'news'数组")
        return
    
    news_items = data['news']
    if not news_items:
        print("没有新闻数据可写入")
        return
    
    # 如果没有指定文件路径，使用默认路径
    if not file_path:
        # 获取当前日期，格式为YYMMDD
        current_date = datetime.datetime.now().strftime("%y%m%d")
        # 构建默认文件路径
        default_dir = Path("news_data_store/test_data")
        file_path = default_dir / f"data_{current_date}_raw.csv"
    else:
        file_path = Path(file_path)
    
    # 确保目录存在
    os.makedirs(file_path.parent, exist_ok=True)
    
    # 检查文件是否存在
    file_exists = file_path.exists()
    
    # 获取表头（新闻数据的所有字段加上来源和可信度）
    fieldnames = list(news_items[0].keys()) + ['source', 'credible']
    
    # 打开文件并写入数据
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # 如果文件不存在，添加表头
        if not file_exists:
            writer.writeheader()
        
        # 写入每条新闻数据
        for news_item in news_items:
            # 添加来源和可信度信息
            row_data = news_item.copy()
            row_data['source'] = source
            row_data['credible'] = credible
            writer.writerow(row_data)
    
    print(f"成功将 {len(news_items)} 条新闻数据保存到 {file_path}")
    return file_path
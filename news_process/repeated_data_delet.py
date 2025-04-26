import csv
import json
from collections import defaultdict
from bots.repNews_delet_bot import bot_delet_repeated_news

def save_clean_data(original_path, clean_data):
    """保存清洗后的数据到原CSV文件"""
    # 定义CSV字段顺序（与原文件保持一致）
    fieldnames = ['company', 'title', 'time', 'summary', 'sourceURL', 'label', 'source', 'credible', 'overlapCount']

    with open(original_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # 按原始字段顺序写入清洗后的数据
        for record in clean_data:
            writer.writerow({
                'company': record['company'],
                'title': record['title'],
                'time': record['time'],
                'summary': record['summary'],
                'sourceURL': record['sourceURL'],
                'label': record['label'],
                'source': record['source'],
                'credible': record['credible'],
                'overlapCount': record.get('overlapCount', 0)  # 使用get方法，如果不存在则默认为0
            })
    print(f'数据已保存至：{original_path}')

def group_company_records(csv_path):
    company_group = defaultdict(list)
    all_clean_records = []  # 存储最终要保存的所有记录
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # 第一阶段：收集原始数据
        for row in reader:
            cleaned = {
                'company': row['company'].strip(),
                'title': row['title'].strip(),
                'time': row['time'].strip(),
                'summary': row['summary'].strip(),
                'sourceURL': row['sourceURL'].strip(),
                'label': row['label'].strip(),
                'source': row['source'].strip() or "无来源",
                'credible': row['credible'].strip(),
                # 'overlapCount': row['overlapCount'].strip()
            }
            company_group[cleaned['company']].append(cleaned)
    
    # 第二阶段：处理分组数据
    for company, records in company_group.items():
        if len(records) == 1:
            # 单记录公司直接保留
            records[0]['overlapCount'] = 1
            all_clean_records.extend(records)
            continue
            
        # 多记录公司进行去重处理
        print(f"处理重复公司：{company}")
        content = json.dumps({"records": records}, ensure_ascii=False)
        deduplicated_data = bot_delet_repeated_news(content=content)
        print(deduplicated_data)
        print("--------------------------------")
        try:
            # 解析去重后的JSON数据
            parsed = json.loads(deduplicated_data)
            deduplicated_records = parsed.get("records", [])
            
            # 添加去重后的记录，确保每条记录都有overlapCount字段
            if deduplicated_records:
                for record in deduplicated_records:
                    if 'overlapCount' not in record:
                        record['overlapCount'] = 0
                all_clean_records.extend(deduplicated_records)
                print(f"去重后保留 {len(deduplicated_records)} 条记录")
            else:
                print("警告：去重后无有效记录，保留原始数据")
                for record in records:
                    record['overlapCount'] = 0
                all_clean_records.extend(records)
        except json.JSONDecodeError:
            print("错误：去重数据格式异常，保留原始数据")
            for record in records:
                record['overlapCount'] = 0
            all_clean_records.extend(records)
    
    # 第三阶段：保存最终数据
    save_clean_data(csv_path, all_clean_records)
    return csv_path

if __name__ == "__main__":
    group_company_records('news_data_store/test_data/raw_data_250415.csv')    
from bots.data_extract_bot import bot_extract_news_data
from data_collection.aggregation_collector import AggregationCollector
from utils.save_to_csv import save_to_csv
from news_process.repeated_data_delet import group_company_records
from news_process.same_company_merge import sort_by_company
from data_publish.googleSheet_upload import upload_csv
import datetime
from pathlib import Path
import pandas as pd

def test_collector(data_save_path = None):
    # 初始化采集器
    # collector = UnifiedCollector()
    collector = AggregationCollector()
    # 存储所有结果
    results = []
    
    # 处理每个URL
    for source_dict in url_list:
        print(f"\n正在采集: {source_dict['source']} ({source_dict['accessWay']})")
        result = collector.collect(source_dict)
        results.append(result)
        
        # 打印采集结果
        if result['status'] == 'success':
            # 如果采集成功，则进行信息抽取
            print(f"  采集成功 ✅ | 内容长度: {len(result['content'])}字符")
            content_preview = result['content'][:5000]
            json_str_result = bot_extract_news_data(content_preview)
            # 保存到 csv 中
            save_to_csv(json_str_result, source_dict['source'], source_dict['credible'],data_save_path)
            # content_preview = result['content'][:5000] + "..." if len(result['content']) > 500 else result['content']
            # json_str_result = extract_news_data(content_preview)
            # print(f"  内容预览: \n{content_preview[:1000]}")
            print(f"  提取的新闻数据: \n{json_str_result}")
        else:
            # 采集失败，跳过
            print(f"  采集失败 ❌ | 错误来源：{source_dict['source']} ，错误: {result.get('error', '未知错误')}")
        
        print("="*50)
    
    # 返回所有结果，方便后续处理
    return results

def filter_news(file_path, days=2):
    """
    过滤掉指定天数前的新闻数据
    
    参数:
        file_path: CSV文件路径
        days: 保留最近几天的数据（默认2天）
    """
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 计算截止日期
    today = datetime.datetime.now()
    cutoff_date = today - datetime.timedelta(days=days)
    
    # 将时间列转换为datetime类型
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    
    # 过滤掉早于截止日期的数据
    filtered_df = df[df['time'] >= cutoff_date]
    
    # 计算被过滤的行数
    filtered_count = len(df) - len(filtered_df)
    print(f"过滤掉了{filtered_count}条过期新闻，保留{len(filtered_df)}条新闻")
    
    # 将过滤后的数据保存回原文件
    filtered_df.to_csv(file_path, index=False)


if __name__ == "__main__":
    # 删除旧文件
    current_date = datetime.datetime.now().strftime("%y%m%d")
    # 构建默认文件路径
    default_dir = Path("news_data_store/test_data")
    file_path = default_dir / f"data_{current_date}_raw.csv"
    
    # 判断文件是否存在，有则删除
    if file_path.exists():
        file_path.unlink()
        print(f"已删除现有文件: {file_path}")

    url_list = [
        {"source": "https://www.aicpb.com/news","accessWay": "http","credible":"no"},
        {"source": "https://sanhua.himrr.com/daily-news/feed","accessWay": "rss","credible":"no"},
        {"source": "https://ai-bot.cn/daily-ai-news/","accessWay": "http","credible":"no"},
        # {"source": "https://www.aibase.com/zh/news","accessWay": "http","credible":"no"},
        # {"source": "https://www.aicpb.com/news","accessWay": "http","credible":"no"},
    ]

    test_results = test_collector() #"news_data_store/test_data/test_data_250407.csv"
    
    # 统计成功/失败数量
    success_count = sum(1 for r in test_results if r['status'] == 'success')
    failed_count = len(test_results) - success_count
    
    print(f"\n采集统计: 总计 {len(test_results)} 个URL, 成功 {success_count} 个, 失败 {failed_count} 个")



    # 过滤掉两天前的news
    filter_news(file_path, days=2)
    # 排序、去重
    sort_by_company(file_path)
    group_company_records(file_path)

    upload_csv(file_path)






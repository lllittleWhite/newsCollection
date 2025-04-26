import time
from datetime import datetime, timedelta
from pytrends.request import TrendReq

def get_google_trends(keyword, start_date_str, end_date_str, geo=''):
    """使用pytrends库获取Google趋势数据
    
    参数:
    - keyword: 搜索关键词
    - start_date_str: 开始日期
    - end_date_str: 结束日期
    - geo: 地区代码，''(全球), 'CN'(中国), 'US'(美国)
    """
    try:
        # 初始化pytrends
        pytrends = TrendReq(hl='zh-CN', tz=480)
        
        # 创建时间框架字符串
        timeframe = f'{start_date_str} {end_date_str}'
        
        # 构建有效载荷
        pytrends.build_payload(kw_list=[keyword], cat=0, timeframe=timeframe, geo=geo)
        
        # 获取兴趣随时间变化数据
        interest_over_time_df = pytrends.interest_over_time()
        
        if interest_over_time_df.empty:
            print(f"关键词 '{keyword}' 在 {geo if geo else '全球'} 区域内没有足够的数据")
            return None
        
        # 提取日期和值
        result = []
        for date, row in interest_over_time_df.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            value = row[keyword]
            result.append((date_str, value))
        
        return result
        
    except Exception as e:
        print(f"获取关键词 '{keyword}' 在 {geo if geo else '全球'} 区域的趋势数据失败: {str(e)}")
        return None

def get_region_name(geo):
    """获取地区名称"""
    if geo == '':
        return '全球'
    elif geo == 'CN':
        return '中国'
    elif geo == 'US':
        return '美国'
    else:
        return geo

def main(keywords):
    """获取最近一周的Google趋势数据并打印"""
    # 计算最近一周的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)  # 一周是7天，所以减6
    
    # 转换为Google趋势API所需的格式
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # 需要获取数据的地区列表
    regions = ['', 'CN', 'US']  # 全球、中国、美国
    
    print(f"获取从 {start_date_str} 到 {end_date_str} 的Google趋势数据")
    
    for keyword in keywords:
        print(f"\n===== 关键词: '{keyword}' =====")
        
        for geo in regions:
            region_name = get_region_name(geo)
            print(f"\n正在获取 {region_name} 的 '{keyword}' 数据...")
            
            results = get_google_trends(keyword, start_date_str, end_date_str, geo)
            
            if results:
                print(f"\n关键词: {keyword} ({region_name})")
                print(f"日期范围: {start_date_str} 至 {end_date_str}")
                print("日期\t\t指数")
                print("-" * 30)
                for date, value in results:
                    print(f"{date}\t{value}")
            else:
                print(f"未能获取关键词 '{keyword}' 在 {region_name} 的数据")
            
            # 添加延迟，避免被API限制
            time.sleep(3)
    
    print("\n程序运行结束！")

if __name__ == "__main__":
    # 要搜索的关键词，可以输入一个列表
    keywords = ['llama4']
    main(keywords)

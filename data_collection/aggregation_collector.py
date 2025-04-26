from data_collection.http_collector.unified_collector import UnifiedCollector
from data_collection.spider_collector.raw_web_spy_get import fetch_webpage_content, process_html

class AggregationCollector:
    """
    整合采集器，根据来源的访问方式选择不同的采集方法
    """
    
    def __init__(self):
        """初始化整合采集器"""
        self.unified_collector = UnifiedCollector()
    
    def collect(self, source_dict):
        """
        根据source_dict中的accessWay字段选择合适的采集方法
        
        Args:
            source_dict: 包含sourceUrl、accessWay和credible的字典
            
        Returns:
            dict: 采集结果，包含以下字段:
                - status (str): 采集状态，'success'或'failed'
                - content (str): 成功时返回处理后的内容
                - error (str): 失败时返回错误信息
                - source (dict): 原始输入的source_dict
        """
        url = source_dict.get("source")
        access_way = source_dict.get("accessWay", "").lower()
        
        if not url or not access_way:
            return {
                "status": "failed",
                "error": "缺少必要参数source或accessWay",
                "content": None,
                "source": source_dict
            }
        
        result = {}
        
        # 根据accessWay选择采集方法
        if access_way in ["http", "rss"]:
            # 使用UnifiedCollector处理HTTP和RSS
            collector_result = self.unified_collector.collect_from_dict(source_dict)
            result = {
                "status": collector_result["status"],
                "content": collector_result.get("content"),
                "error": collector_result.get("error"),
                "source": source_dict
            }
            
        elif access_way == "spider":
            # 使用raw_web_spy_get处理需要浏览器渲染的页面
            spider_result = fetch_webpage_content(url)
            
            if spider_result["status"] == "success":
                # 处理HTML内容
                processed_content = process_html(spider_result["content"], url)
                
                result = {
                    "status": "success",
                    "content": processed_content,
                    "error": None,
                    "source": source_dict
                }
            else:
                result = {
                    "status": "failed",
                    "content": None,
                    "error": spider_result["error"],
                    "source": source_dict
                }
        else:
            # 不支持的accessWay
            result = {
                "status": "failed",
                "content": None,
                "error": f"不支持的访问方式: {access_way}",
                "source": source_dict
            }
        
        return result


if __name__ == "__main__":
    # 测试整合采集器
    collector = AggregationCollector()
    
    # 测试HTTP采集
    http_source = {
        "sourceUrl": "https://www.aicpb.com/news",
        "accessWay": "http",
        "credible": "no"
    }
    
    http_result = collector.collect(http_source)
    print(f"\nHTTP采集结果: {http_source['sourceUrl']}")
    print(f"  状态: {'成功 ✅' if http_result['status'] == 'success' else '失败 ❌'}")
    if http_result['status'] == 'success':
        print(f"  内容长度: {len(http_result['content'])}字符")
    else:
        print(f"  错误: {http_result['error']}")
    
    # 测试Spider采集
    spider_source = {
        "sourceUrl": "https://openai.com/blog",
        "accessWay": "spider",
        "credible": "yes"
    }
    
    spider_result = collector.collect(spider_source)
    print(f"\nSpider采集结果: {spider_source['sourceUrl']}")
    print(f"  状态: {'成功 ✅' if spider_result['status'] == 'success' else '失败 ❌'}")
    if spider_result['status'] == 'success':
        print(f"  内容长度: {len(spider_result['content'])}字符")
    else:
        print(f"  错误: {spider_result['error']}")

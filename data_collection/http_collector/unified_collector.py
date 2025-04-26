import requests
from bs4 import BeautifulSoup, NavigableString
import random
import time
from urllib.parse import urljoin

class UnifiedCollector:
    """统一的网页和RSS内容采集器"""
    
    def __init__(self, delay_min=1, delay_max=3):
        """初始化采集器
        
        Args:
            delay_min: 请求间隔最小秒数
            delay_max: 请求间隔最大秒数
        """
        self.delay_min = delay_min
        self.delay_max = delay_max
        
        # 统一的请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
    
    def fetch_content(self, url, timeout=10, is_rss=False):
        """获取URL内容
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
            is_rss: 是否为RSS链接
            
        Returns:
            dict: 包含url、content/error和status的字典
        """
        try:
            request_params = {
                'headers': self.headers,
                'timeout': timeout
            }
            
            # 对于非RSS链接添加cookies和stream参数
            if not is_rss:
                request_params['cookies'] = {'session_id': 'dummy_session_123'}
                request_params['allow_redirects'] = True
            else:
                request_params['stream'] = True
                
            response = requests.get(url, **request_params)
            response.raise_for_status()
            
            # 处理编码
            if is_rss and 'charset' in response.headers.get('content-type', '').lower():
                encoding = response.encoding
            else:
                encoding = 'utf-8'
            
            content = response.content.decode(encoding, errors='replace')
            
            return {
                "url": url,
                "content": content,
                "status": "success"
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }
    
    def process_html(self, content, base_url):
        """处理HTML内容
        
        Args:
            content: HTML原始内容
            base_url: 基础URL，用于转换相对链接
            
        Returns:
            str: 处理后的内容
        """
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            # 清理不需要的元素
            for tag in soup(['img', 'script', 'style', 'iframe', 'noscript']):
                tag.decompose()
            
            processed = []
            
            for element in soup.descendants:
                if isinstance(element, NavigableString):
                    if (text := element.strip()):
                        processed.append(text)
                elif element.name == 'a':
                    if (link_text := element.get_text(strip=True)) and (href := element.get('href')):
                        absolute_url = urljoin(base_url, href)
                        processed.append(f"[{link_text}]({absolute_url})")
            
            return ' '.join(processed)
        except Exception as e:
            return f"HTML处理错误: {str(e)}\n原始内容: {content[:500]}..."
    
    def collect_from_dict(self, source_dict):
        """根据字典信息采集内容
        
        Args:
            source_dict: 包含source和accessWay的字典
            
        Returns:
            dict: 采集结果，包含以下字段:
                - status (str): 采集状态，'success'或'failed'
                - content (str): 成功时返回处理后的内容
                - error (str): 失败时返回错误信息
        """
        url = source_dict.get("source")
        access_way = source_dict.get("accessWay")
        
        if not url or not access_way:
            return {
                "error": "缺少必要参数source或accessWay",
                "status": "failed"
            }
        
        # 根据accessWay判断是RSS还是HTTP
        is_rss = access_way.lower() == "rss"
        
        # 添加随机延时
        time.sleep(random.uniform(self.delay_min, self.delay_max))
        
        # 获取内容
        result = self.fetch_content(url, is_rss=is_rss)
        
        # 如果是HTTP，则处理HTML内容
        if result["status"] == "success" and not is_rss:
            result["content"] = self.process_html(result["content"], url)
            
        # 只返回需要的字段
        return {
            "status": result["status"],
            "content": result.get("content"),
            "error": result.get("error")
        }
    

if __name__ == "__main__":
    # 测试统一采集器
    collector = UnifiedCollector()
    
    # 使用字典测试
    source_dict = {
        "source": "https://www.aicpb.com/news",
        "accessWay": "http",
        "credible": "no"
    }
    
    result = collector.collect_from_dict(source_dict)
    
    print(f"\n采集结果：{result['url']} ({'RSS' if result['source']['accessWay'].lower() == 'rss' else '网页'})")
    
    if result['status'] == 'success':
        print(f"  采集成功 ✅ | 有效内容长度：{len(result['content'])}字符")
        print("="*40)
        print(result['content'][:1000])
    else:
        print(f"  采集失败 ❌ | {result['error']}")
    
    # 再测试一个RSS源
    rss_dict = {
        "source": "https://sanhua.himrr.com/daily-news/feed",
        "accessWay": "rss",
        "credible": "yes"
    }
    
    rss_result = collector.collect_from_dict(rss_dict)
    
    print(f"\n采集结果：{rss_result['url']} ({'RSS' if rss_result['source']['accessWay'].lower() == 'rss' else '网页'})")
    
    if rss_result['status'] == 'success':
        print(f"  采集成功 ✅ | 有效内容长度：{len(rss_result['content'])}字符")
        print("="*40)
        print(rss_result['content'][:1000])
    else:
        print(f"  采集失败 ❌ | {rss_result['error']}")
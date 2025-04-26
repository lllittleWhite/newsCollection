from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import re

def fetch_webpage_content(url):
    """
    通用网页内容获取函数，返回指定URL的原始网页内容
    
    Args:
        url (str): 需要获取内容的网页URL
        
    Returns:
        dict: 包含以下字段:
            - status (str): 采集状态，'success'或'failed'
            - content (str): 成功时返回网页HTML内容
            - error (str): 失败时返回错误信息
    """
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 启动WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 访问网页
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 获取网页的HTML内容
        page_content = driver.page_source
        
        return {
            "status": "success",
            "content": page_content,
            "error": None
        }
        
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        return {
            "status": "failed", 
            "content": None,
            "error": error_msg
        }
    finally:
        driver.quit()

def process_html(content: str, base_url: str) -> str:
    """处理HTML内容，保留文本和链接，移除图片等无关元素"""
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

if __name__ == "__main__":
    # 测试示例
    url = "https://openai.com/news"
    # url = "https://www.anthropic.com/news"
    content = fetch_webpage_content(url)
    
    if content["status"] == "success":
        print("成功获取网页内容")
        
        # 处理HTML内容
        processed_content = process_html(content["content"], url)
        
        # 打印处理后的内容
        print("处理后的内容预览:")
        print(processed_content[:2000] + "...")
        
    else:
        print(f"获取网页内容失败: {content['error']}")

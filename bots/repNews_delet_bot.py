import openai

def llmReturn_process(llm_return: str) -> str:
    """
    数据处理函数，处理LLM返回的数据，使其处理为能直接读取的json数据
    
    参数:
    web_content -- 待处理的新闻文本内容
    
    返回:
    处理后的新闻文本内容
    """
    return llm_return

def bot_delet_repeated_news(content: str, api_key: str = "sk-rdc-botplatform-2024020473", base_url: str = "https://chat.inhyperloop.com/v1") -> str:
    """
    重复信息处理函数
    
    参数:
    web_content -- 待处理的新闻文本内容
    api_key -- OpenAI API密钥（默认使用内置测试密钥）
    base_url -- API基础URL
    
    返回:
    结构化的JSON格式新闻数据
    """
    # 初始化OpenAI客户端
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    sys_instruct = """你是一个专业级AI新闻json去重引擎，请严格按照以下规则执行重复信息删除：

		1. **信息去重策略**
		- 根据json信息，判断信息是否讲同一件事
		- 如果多个json均是报道同一件事，删除summary信息更简略所有的json，只保留一条信息详细的json
		
		2. **输出格式规则**
        - 不修改原文内容
		- 输出时保留输入的信息的格式，只做删除处理，不输出额外信息
        - 统计重复信息数量，并输出在overlapCount字段中，填阿拉伯数字即可，无需单位
    """
    
    user_content = f'''请分析以下若干新闻数据"{content}"，对相同信息进行去重处理,请保留原格式只做删除处理，同时在每条记录中添加overlapCount重复信息数量，严格输出成一个二级json，请勿输出多余内容：
    {{
        "records": [
            {{
                "company": "",
                "title": "",
                "time": "",
                "summary": "",
                "source": "",
                "label": "",
                "sourceURL": "",
                "overlapCount": "" // 重复信息数量，填阿拉伯数字即可，无需单位，如果只有一条记录，则填1，如果有2条意思相同记录，则填2，以此类推
            }},
            {{
                "company": "",
                "title": "",
                "time": "",
                "summary": "",
                "source": "",
                "label": "",
                "sourceURL": "",
                "overlapCount": ""
            }},
        ]
    }}'''
    
    try:
        # 调用OpenAI聊天API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_instruct},
                {"role": "user", "content": user_content}
            ],
            temperature=0
        )
        
        return completion.choices[0].message.content
    
    except openai.APIError as e:
        print(f"API请求失败: {e}")
        return "{}"
    except Exception as e:
        print(f"发生未知错误: {e}")
        return "{}"

# 使用示例
if __name__ == "__main__":
    sample_content = '''
谷歌,谷歌 Gemini 新功能：Canvas 和 Audio Overview,2025-03-19,谷歌 Gemini APP 发布 Canvas 和 Audio Overview 新功能，Canvas 协同工作完善文档、编写代码、设计原型，Audio Overview 将文件转化为播客式音频讨论。,https://sanhua.himrr.com/daily-news/feed,Gemini，协作功能，应用更新,https://blog.google/products/gemini/gemini-collaboration-features/
谷歌,谷歌 Gemini APP 更新,2025-03-14,谷歌 Gemini APP 发布更新，2.0 Flash Thinking Experimental 版本提升推理能力和响应速度，Deep Research 功能升级，新增 Gems 功能允许创建专属 AI 智能体。,https://sanhua.himrr.com/daily-news/feed,Gemini，AI智能体，应用更新,https://blog.google/products/gemini/new-gemini-app-features-march-2025/
谷歌,谷歌 Gemini 更新：新增音频播客、Canvas 画布与 Deep Research 扩容,2024-03-19,谷歌Gemini最新推出了 Canvas 功能，可用于创建、改进和分享写作与编码项目，实时预览代码效果。新增“文本转音频”功能（Audio Overviews），可将文本对话生成音频播客。免费用户的 Deep Research 使用次数增加至每月 10 次，帮助用户更高效地完成复杂的研究任务。,https://ai-bot.cn/daily-ai-news/,Gemini，多模态，音频播客,https://blog.google/products/gemini/gemini-collaboration-features/
谷歌,谷歌达成迄今最大一笔收购交易，320 亿美元现金买下云安全公司 Wiz,2024-03-19,谷歌宣布以320亿美元全现金收购云安全初创公司Wiz，是其迄今最大一笔收购交易。Wiz是一家总部位于纽约的云安全公司，提供连接到所有主要云服务和代码环境的安全平台。此次收购旨在提升谷歌云的安全能力，支持多云环境，推动云安全创新。,https://ai-bot.cn/daily-ai-news/,谷歌，Wiz，云安全,https://www.ithome.com/0/838/834.htm
谷歌,谷歌 Gemini 2.0 Flash 模型拥有强大图片去水印功能，或触犯版权红线,2024-03-17,谷歌推出的 Gemini 2.0 Flash 模型因强大的图片去水印功能引发争议。模型可去除包括盖蒂图片社等知名图库图片的水印，会填补因水印删除产生的空白区域，目前免费提供给用户使用。,https://ai-bot.cn/daily-ai-news/,Gemini 2.0 Flash，图片处理，去水印,https://www.ithome.com/0/838/290.htm
'''
    result = bot_delet_repeated_news(content=sample_content)
    print(result)
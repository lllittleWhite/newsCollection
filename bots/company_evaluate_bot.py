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

def bot_evaluate_company(content: str, api_key: str = "sk-rdc-botplatform-2024020473", base_url: str = "https://chat.inhyperloop.com/v1") -> str:
    """
    公司评级打分函数
    
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
    
    sys_instruct = """你是一个专业级AI公司评级打分员，请严格按照公司梯度表进行公司评分：
		第一梯队打10分：openai,谷歌,DeepSeek,Anthropic(claude系列)
        第二梯队打8分：xAI(Grok系列),阿里巴巴,Meta(Llama系列),Midjourney
        第三梯队打6分：字节跳动,kimi|月之暗面,智谱清言|智普AI|GLM系列,可灵|可灵AI|可灵大模型
        第四梯队打4分：腾讯、华为、星火大模型、英伟达
        第五梯队打2分：相对知名，但未上榜
        第六梯队打1分：不知名
    """
    
    user_content = f'''请分析以下若干新闻数据"{content}"，对公司级别进行打分，请保留原格式只做打分处理，在每条记录中添加"companyScore"项并打上分数，严格输出成json格式，请勿输出多余内容：
        {{
            "company": "",
            "title": "",
            "time": "",
            "summary": "",
            "source": "",
            "label": "",
            "sourceURL": "",
            "credibel": "",
            "overlapCount": "",
            "companyScore": ""  // 公司评分，填阿拉伯数字即可，无需单位
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
    谷歌,Gemini更新API文档支持MCP协议,2025-04-07,Gemini更新API文档，宣布支持MCP协议，仅用4天时间完成部署。,无来源,"Gemini, API更新, MCP协议",https://www.aicpb.com/news,no,1
    '''
    result = bot_evaluate_company(content=sample_content)
    print(result)
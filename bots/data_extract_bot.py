from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def llmReturn_process(llm_return: str) -> str:
    """
    数据处理函数，当前直接返回，可以根据业务需求扩展json解析校验等功能。
    """
    return llm_return

def bot_extract_news_data(web_content: str, api_key: str = "",
                      base_url: str = "") -> str:
    """
    使用LangChain实现的新闻数据抽取函数。

    参数:
    web_content -- 待处理的新闻内容
    api_key -- OpenAI API密钥
    base_url -- api基础URL地址

    返回:
    结构化的JSON格式新闻数据
    """

    # Step1: 配置Chat模型接口 (LLM)
    llm = ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=base_url,
        model_name="gpt-4o-mini",
        temperature=0,
        # max_tokens=10000,  # 设置输出最大token数
        max_retries=3,    # 设置最大重试次数
        request_timeout=30  # 设置请求超时时间（秒）
    )

    # Step2: 设置系统指令模板(System Prompt)，明确执行规则
    system_template = '''你是一个专业级AI新闻结构化处理引擎，能够从杂乱的信息源中抽取结构化ai新闻信息，请严格按照以下规则执行信息抽取：

    1. 实体识别规则
    - company优先选公司/机构，如果没有则使用新闻中的产品/模型名。
    - `company`字段：提取时，采用最官方公司的名字，而不是旗下团队或实验室名称，如新闻中是“字节”，则填“字节跳动”，而不是“字节”；如“阿里通义”、“阿里通义团队”、“阿里”则填“阿里巴巴”
    - `company`字段：如果是很有名的产品，新闻中未出现公司名，如“ChatGPT”、“gemini“等，则填“OpenAI”、“谷歌”等官方公司名字。

    2. 时间标准化规则
    - 明确则采用文中日期，无具体日期则采用文档发布时间，默认为2025年，如无的信息则填"无时间"。

    3. 摘要生成规范
    - 聚焦核心突破，去除冗余信息，保留关键技术参数。

    4. 标签生成策略
    - 模型/产品名称、模型功能（如文本生成、多模态、语言模型）、产品特征最多5个标签。

    5. 数据过滤策略
    - 仅关注AI领域的产品/模型上线与更新，忽略与ai无关内容。

    6. 内容排序规范
    - 时间从新到旧排序输出。
    '''

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    # Step3: 定义User Prompt用于动态接收输入新闻
    human_template = '''请分析以下新闻数据内容:{content}, 提取实体信息并严格按照下面的json格式输出，请勿输出多余内容：

    {{
        "news": [
            {{
                "company": "",       // 实体类型[优先公司/机构，其次产品/模型名]
                "title": "",         // 保留关键点的简短标题
                "time": "",          // yyyy-MM-dd格式
                "summary": "",       // 技术概要、如支持语言数量、精度指标等
                "sourceURL": "",     // 文中新闻来源链接URL，若无则填"无来源"
                "label": ""          // 模型或产品名与模型功能、产品特征标签(最多3个标签，用逗号分隔)
            }},
            ... // 更多新闻项
        ]
    }}'''

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Step4: 创建完整Prompt模板 (AI指令 + 人类输入混合 Prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    # Step5: 使用新的链式调用方式
    chain = chat_prompt | llm

    # 调用链路并执行
    try:
        chain_response = chain.invoke({"content": web_content})
        return llmReturn_process(chain_response.content)
    except Exception as e:
        error_message = f"新闻数据抽取过程中发生错误: {str(e)}"
        print(error_message)
        return '{"news": [], "error": "' + error_message + '"}'


# 使用示例
if __name__ == "__main__":
    test_content = "测试新闻内容..."
    try:
        result = bot_extract_news_data(web_content=test_content)
        print(result)
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
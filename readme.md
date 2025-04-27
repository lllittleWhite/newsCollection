# ai——news自动采集

## 1 介绍

程序主要由三个部分组成，数据采集（data_collection）、新闻处理（news_process）、新闻发布（data_publish）组成。还有两个额外的工具包，分别是 写好提示词的llm（bots）、用来保存csv文件的程序（utils/save_to_csv.py）。新闻排序（news_rerank）。

## 2 采集流程

程序输入为字典列表，例：
    url_list = [
        {"source": "https://www.aicpb.com/news","accessWay": "http","credible":"no"},
        {"source": "https://sanhua.himrr.com/daily-news/feed","accessWay": "rss","credible":"no"},
        {"source": "https://ai-bot.cn/daily-ai-news/","accessWay": "http","credible":"no"},
    ]
包含：信息源，获取方式（accessWay），信息源是否可信（credible）

程序遍历url_list，将单条字典输入到采集器中，采集器根据accessWay来选择不同的采集方式，采集完单个信息源原始新闻信息后，将数据输入到llm中，进行数据抽取，抽取成机构化json信息：
    {
        "news": [
            {
                "company": "",       // 实体类型[优先公司/机构，其次产品/模型名]
                "title": "",         // 保留关键点的简短标题
                "time": "",          // yyyy-MM-dd格式
                "summary": "",       // 技术概要、如支持语言数量、精度指标等
                "sourceURL": "",     // 文中新闻来源链接URL，若无则填"无来源"
                "label": ""          // 模型或产品名与模型功能、产品特征标签(最多3个标签，用逗号分隔)
            },
            ... // 更多新闻项
        ]
    }

抽取完成后输入到将json数据写入csv文件中，同时加上source和credible，例：
OpenAI,OpenAI宣布ChatGPT新功能，新增长期记忆功能,2025-04-11,OpenAI推出ChatGPT的新功能，能引用过去所有聊天记录，提供更加私人订制的体验。,https://mp.weixin.qq.com/s/NLixAJp8bfUsPgNPUMAaJw,"ChatGPT,记忆功能,私人助理",https://ai-bot.cn/daily-ai-news/,no

初步采集后，进行数据处理，首先将相同的公司名的新闻信息，进行重新排序。
排完序后，若一家公司有多条新闻，则有可能新闻中有重复的信息，将同一家公司的所有新闻均输入到llm，将新闻进行去重处理，并统计重复新闻条数。

最后是信息发布，将最后保存了新闻数据的csv数据上传至google sheet，通过make中的webhook分享google sheet 链接至slack频道中。


## 3 主要模块介绍

### 3.1 数据采集

数据采集由多个不同类型的采集器组成，分别用来采集不同来源渠道的信息。http_collector用来采集无严格反爬的网页和rss信息源信息；email_collector用来采集邮件订阅的新闻信息；spider_collector用来采集反爬策略较为严格的网页信息。

data_collection/aggregation_collector.py是一个整合后的抽象层，可以根据输入自动选择相应的采集器。

### 3.2 新闻处理

新闻处理由两步组成：news_process/same_company_merge.py 可以将同一家公司的新闻排在一起，不对新闻内容做任何处理，仅做排序处理；news_process/repeated_data_delet.py 将同一家的新闻输入到llm中，使其删除重复的新闻，并统计重复的数量，可用于后续的新闻排序。处理后的数据在news_data_store/test_data 文件夹下，data_250415_raw.csv 文件数字为当天日期。

### 3.3 新闻发布

将csv上传至google sheet，并将新建的sheet链接通过make发送到slack频道。
注意token.json文件可能会过期导致无法上传到google sheet，只需删除token.json后重新运行程序，程序会自动打开浏览器，手动授权即可，授权时要勾选可以创建google driver中的文件的权限。

### 3.4 bots

bots中有三个写好提示词的bot，bots/data_extract_bot.py 用来从采集到的原始新闻数据中提取结构化的新闻数据；bots/repNews_delet_bot.py 用来删除重复的新闻数据，并统计重复个数；bots/company_evaluate_bot.py给新闻涉及的公司进行评分，以便后续排序。

## 4 新闻排序

设计多个评价维度，对新闻重要程度进行评价，最后得到一个分数，根据分数对新闻进行排序。

三个较好实现的维度：
    （1）公司知名度：在prompt中给llm一份ai公司梯度表，让llm对新闻的该维度进行评分
    （2）新闻重叠度：采集的新闻来自多个来源，我们设想同一条新闻被多个来源报道了，则说明该新闻可能较为重要，报道来源越多，评分越高
    （3）谷歌热搜指数：谷歌热搜指数越高，则说明该新闻关注度越高，可能更为重要

权重设计：
    设计权重来综合所有评价维度对新闻进行评分排序

import requests
import json
import os
from datetime import datetime, timedelta

# 解码函数
def decrypt(ptbk, index_data):
    n = len(ptbk)//2
    a = dict(zip(ptbk[:n], ptbk[n:]))
    return "".join([a[s] for s in index_data])

# 获取数据源
def get_index_data(keys, start_date, end_date):
    words = [[{"name": keys, "wordType": 1}]]
    words = str(words).replace(" ", "").replace("'", "\"")
    url = f'http://index.baidu.com/api/SearchApi/index?area=0&word={words}&startDate={start_date}&endDate={end_date}'
    # 请求头配置
    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cipher-Text": "1698156005330_1698238860769_ZPrC2QTaXriysBT+5sgXcnbTX3/lW65av4zgu9uR1usPy82bArEg4m9deebXm7/O5g6QWhRxEd9/r/hqHad2WnVFVVWybHPFg3YZUUCKMTIYFeSUIn23C6HdTT1SI8mxsG5mhO4X9nnD6NGI8hF8L5/G+a5cxq+b21PADOpt/XB5eu/pWxNdwfa12krVNuYI1E8uHQ7TFIYjCzLX9MoJzPU6prjkgJtbi3v0X7WGKDJw9hwnd5Op4muW0vWKMuo7pbxUNfEW8wPRmSQjIgW0z5p7GjNpsg98rc3FtHpuhG5JFU0kZ6tHgU8+j6ekZW7+JljdyHUMwEoBOh131bGl+oIHR8vw8Ijtg8UXr0xZqcZbMEagEBzWiiKkEAfibCui59hltAgW5LG8IOtBDqp8RJkbK+IL5GcFkNaXaZfNMpI=",
        "Referer": "https://index.baidu.com/v2/main/index.html",
        "Accept-Language": "zh-CN,zh;q=0.9",
        'Cookie': Cookie}
    res = requests.get(url, headers=headers)
    res_json = res.json()
    
    if res_json["message"] == "bad request":
        print("抓取关键词："+keys+" 失败，请检查cookie或者关键词是否存在")
        return None, None
    else:
        # 获取特征值
        data = res_json['data']
        uniqid = data["uniqid"]
        url = f'http://index.baidu.com/Interface/ptbk?uniqid={uniqid}'
        res = requests.get(url, headers=headers)
        # 获取解码字
        ptbk = res.json()['data']
        return res_json, ptbk

# 解析数据
def parse_data(res_json, ptbk):
    data = res_json['data']
    result = []
    
    for userIndexe in data['userIndexes']:
        name = userIndexe['word'][0]['name']
        index_all = userIndexe['all']['data']
        start_date = userIndexe['all']['startDate']
        
        if index_all == '':
            print(f"关键词 {name} 没有数据")
            continue
            
        try:
            # 解码数据
            index_all_data = []
            for e in decrypt(ptbk, index_all).split(","):
                if e.strip():  # 检查是否为空字符串
                    try:
                        index_all_data.append(int(e))
                    except ValueError:
                        index_all_data.append(0)  # 将无法转换的值设为0
                else:
                    index_all_data.append(0)  # 将空字符串设为0
            
            # 创建日期列表
            date_list = []
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            for _ in range(len(index_all_data)):
                date_list.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
                
            # 将日期和数据组合
            result.append({
                "name": name,
                "data": list(zip(date_list, index_all_data))
            })
        except Exception as e:
            print(f"解析关键词 {name} 数据时出错: {e}")
            
    return result

# 主函数
def main(keys):
    # 计算最近一周的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)  # 一周是7天，所以减6
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"获取从 {start_date_str} 到 {end_date_str} 的百度指数数据")
    
    for key in keys:
        print(f"\n正在获取关键词 '{key}' 的数据...")
        res_json, ptbk = get_index_data(key, start_date_str, end_date_str)
        
        if res_json and ptbk:
            results = parse_data(res_json, ptbk)
            for result in results:
                print(f"\n关键词: {result['name']}")
                print(f"日期范围: {start_date_str} 至 {end_date_str}")
                print("日期\t\t指数")
                print("-" * 30)
                for date, value in result['data']:
                    print(f"{date}\t{value}")
    
    print("\n程序运行结束！")


if __name__ == '__main__':
    # 参数列表
    Cookie = 'BAIDUID_BFESS=97AACD4366AEF067D2E8658CA9E85967:FG=1; BDSVRTM=0; BDUSS=ZFU0hDQVhrZms0RVR2MUlxM3ByNVhQbklKa0pTNkZnS0F0SzM4VWRkVUFtUTFvRUFBQUFBJCQAAAAAAAAAAAEAAAALs~L9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM5mcADOZnVl; BDUSS_BFESS=ZFU0hDQVhrZms0RVR2MUlxM3ByNVhQbklKa0pTNkZnS0F0SzM4VWRkVUFtUTFvRUFBQUFBJCQAAAAAAAAAAAEAAAALs~L9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM5mcADOZnVl; BD_CK_SAM=1; BIDUPSID=97AACD4366AEF067D2E8658CA9E85967; CHKFORREG=42322a37efc755a3efa03011b87cce0e; CPID_212=65368067; CPTK_212=1921233449; HMACCOUNT=78358B88CA0E640F; HMACCOUNT_BFESS=78358B88CA0E640F; H_PS_PSSID=61027_62280_62325_62343_62347_62328_62366_62373_62421_62423_62427_62474_62484_62499; H_WISE_SIDS=61027_62325_62343_62347_62373_62427_62474_62484_62499_62519_62456_62455_62452_62451_62554_62673_62688; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1743651206; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1741768115,1743648586; PSINO=7; PSTM=1741750980; RT="z=1&dm=baidu.com&si=f207cbd1-cfe0-4806-bd6e-743d7faf5669&ss=m90rcf94&sl=a&tt=lda&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=1kd9q"; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04936610355nt0VxV%2FZdF0%2B4ARulxlaC24a3xlD3EePKypPKjgD71D4waXFIzMd2%2Bd%2Fy4UopxRvyZL7vG3y%2FVEt57gLET5ymTSQyfcpgYqIFm4t1aAlVvBg08pzala5dSvgEuOw8xigrmJg8KHBqfzigAITHAUelnXbQEq0y1mh3r2pu0s5HTLUfd%2BAAxIxRKWkTGEPd9uE1URWoMnO3%2Fb8lsmT%2FAI1fIV0BPB6QoqZWR55EITYL5%2FbgwcxiOJlECVBJS%2Fiyz3Xxe2ycqiHQPvSzNx3hkoyaGUY3WEmSwYseEZYIwoHm3A%3D32695342552212735198463179599418; ZFY=nPfEHobGvWsvORwWGFTJj4Y0YW7k0y8iA5mNWJTh1HQ:C; __bsi=10268843738936510301_00_12_R_N_36_0303_c02f_Y; __cas__id__212=65368067; __cas__rn__=493661035; __cas__st__212=042000d19a3fe1345754b22829daf13dd66eec4ffc492405c5c11014a9059a898e6d696dd5bacfb15bc68006; ab_bid=5560820909c6f776d7b9110f71c1a1b8a420; ab_jid=87884575f556378f8df0402037229f556081; ab_jid_BFESS=87884575f556378f8df0402037229f556081; ab_sr=1.0.1_NzMwOWJhN2E2Zjg0YjgxNjM0ZGY5NWMyZDUwYWQ5ODgzZWMzMGZjMTU3YzhhMmEwZTI3OTY4ZDc4ZTJmMDdjNWVmNjIzNjA0ZmUwNWVmODQ3OGZlNWMzZmVhZWFkYzI3OGUxOGMyYjU0OWFhZWIwZGU5YjY2YzE3OGYxYmJkOTgyOGNhOTFhMzk4MzVkNWNkZjI2YzI4ZGZhN2Y0MmM0Yg==; bce-sessionid=001beed7ef12f2b4abc8e7089bfc2b697da; bdindexid=i7g1f4oilqhsa9a69pmu5ech62; delPer=0; ppfuid=FOCoIC3q5fKa8fgJnwzbE0LGziLN3VHbX8wfShDP6RCsfXQp/69CStRUAcn/QmhIlFDxPrAc/s5tJmCocrihdwitHd04Lvs3Nfz26Zt2holplnIKVacidp8Sue4dMTyfg65BJnOFhn1HthtSiwtygiD7piS4vjG/W9dLb1VAdqO71sNtrfJH2UrRokTvezUwO0V6uxgO+hV7+7wZFfXG0MSpuMmh7GsZ4C7fF/kTgmvlMIA/tB2qdnJ8KkulgesR5YKU+qTqtaaBkWIZO5dn/GldC1S4QUhUhpm5KMoOoF81v2iwj13daM+9aWJ5GJCQM+RpBohGNhMcqCHhVhtXpVObaDCHgWJZH3ZrTGYHmi7XJB9z3y2o8Kqxep5XBCsugNOW5C73e/g54kuY4PKIS8TtlheGhftBTbUILzt33xSjQXz/gJEgSYx1vUQMipXdSecr9yhMSRLVoFktEC1isMd3ElTWP2BbqdT6AN6/w9mvK/S9Ff5RtLDcahg8QCqqVSOGmcNGOyyyBLpZo/fmpEgfXgGxCNf3Sx8e4KXUBrqV/g3hEEf9luu8oPziRIwanIJY1XZupqPZgmfh8BLwT9YUuyc0u8RKTitzO23hSwGX7sI4U3M5cfLBwVX5m74NveYUNi7Li87S8ZbXy31eyxBDK4IiDGlt1VFsxDIz0RsVHZudegSJ4zYa95fLOW41HdqdlVsa4ORVPwaoYgWzWigT4KUSvejPWWbczD37o0JAMY0Xq/mt7JbC+fPJzgUfZuCz2j9K2vYqWOhuLA4PHxMvpkKeq17vDXUvsEpMg5fzRV1KthxgfaWac6catjZSHJMc4xeuRg7bfpEY/vwboa87Mf4DRxb3AAPFSzwHIQsKUb2NhurFXPHTBQ0ZqOMmlY+ev7ywybLL8HzYMUKf7xXkuNYCZBWkNbmLJnCAaUcxvvi236pnhRAiCpqFQgkNjC1A5ggMDnpv8k9lbQM2eIu01rzx5KJW22MzZ0c8aSEaiiS5MGq2rHDxd+cheyqXoKDbFUOPsQE72/a0kEWC2KhuPKLM9/6dZ00isWP1M71YVK+GcriYXdSGsdTLua2Z4rsiMpSciOy0GtH0BDIaHROBNUIGus13vk3BD9zddjzj9ZJseUlzwEV+bscicwIjSCwQvM4e3xnzVzlld+zvYN0q7Yw+xx5u95PSoz+nO88s9TqjpS2CuGXeoK3JV0ZsrYL63KbB6FE0u0LGhMX2XqphVNhJG/707P2GcCYlcR4=;'
    keys = ["AutoGLM","chatGPT","GPT4o"]
    
    if Cookie == "":
        Cookie = input("请输入你的Cookie，若错误则无法运行：")
    else:
        main(keys)

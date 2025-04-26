import requests
import msal
import json
import os

# 身份验证凭据
client_id = 'a367d484-d042-433a-acee-cf3f577eded2'
client_secret = 'BXwR.LtAjImWm72nFWx3_~qYpfikg~-R7c'
tenant_id = 'aa5822f5-898e-4310-92bb-5648850ba0e2'
email = 'zekai.wan@ewp-group.com'

# 应用配置
authority = f'https://login.microsoftonline.com/{tenant_id}'
scope = ['https://graph.microsoft.com/Mail.Read']

# 令牌缓存文件
cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_cache.json")

def get_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cache.deserialize(f.read())
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        with open(cache_file, "w") as f:
            f.write(cache.serialize())

def get_access_token():
    """获取访问令牌，优先使用缓存"""
    cache = get_cache()
    
    app = msal.PublicClientApplication(
        client_id,
        authority=authority,
        token_cache=cache
    )
    
    accounts = app.get_accounts()
    if accounts:
        # 优先使用刷新令牌刷新
        result = app.acquire_token_silent(scope, account=accounts[0])
        save_cache(cache)
        if result:
            return result["access_token"]
    
    # 如果没有缓存或刷新失败，则使用设备代码流程
    flow = app.initiate_device_flow(scopes=scope)
    if "user_code" not in flow:
        print("无法创建设备代码流:", flow.get("error"))
        return None
    
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    save_cache(cache)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print("获取令牌失败:", result.get("error"))
        return None

def get_messages(access_token, top=10):
    """获取最近的邮件"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 使用 /me 端点获取当前用户的邮件
    endpoint = 'https://graph.microsoft.com/v1.0/me/messages'
    params = {
        '$top': top,
        '$select': 'subject,receivedDateTime,from,body,hasAttachments,id',
        '$orderby': 'receivedDateTime DESC'
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

def main():
    # 获取访问令牌
    print("正在获取访问令牌...")
    token = get_access_token()
    if not token:
        print("获取访问令牌失败")
        return
    
    print("成功获取访问令牌")
    
    # 获取邮件
    print("正在获取邮件...")
    messages = get_messages(token)
    if not messages:
        print("获取邮件失败")
        return
    
    # 打印原始邮件内容
    print("原始邮件内容:")
    print(json.dumps(messages, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 
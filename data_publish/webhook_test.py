import requests

# Webhook URL
webhook_url = "https://hook.eu2.make.com/82v5ovzta8uuc1k9mvpp3wg0yo1eegrj"

# 要发送的数据
data = {
    "message": "https://docs.google.com/spreadsheets/d/18AGhzSP5cVAXO-33AR_Fxdcwga-QJV20tLIpgDAWsPk/edit?usp=sharing",
    "name": "Test User",
    "timestamp": "2025-4-15 10:30:00"
}

# 发送POST请求
response = requests.post(webhook_url, json=data)

# 检查响应
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")
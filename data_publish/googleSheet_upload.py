import os.path
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
from googleapiclient.http import MediaFileUpload
import requests

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]  # 添加Drive权限用于分享

# Webhook URL
WEBHOOK_URL = "https://hook.eu2.make.com/82v5ovzta8uuc1k9mvpp3wg0yo1eegrj"

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
SAMPLE_RANGE_NAME = "Class Data!A2:E"


def create(title):
  # pylint: disable=maybe-no-member
  try:
    creds = get_credentials()  # 使用公共认证方法
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
    return spreadsheet.get("spreadsheetId")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def get_credentials():
    """ 提取公共认证逻辑 """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "data_publish/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def share_spreadsheet(spreadsheet_id):
    """
    函数已修改，不再设置Google Sheet为公开查看的权限
    仅保留原始权限设置
    """
    # 不再执行权限修改操作
    print(f"保持Spreadsheet {spreadsheet_id} 的默认权限设置")
    return True

def get_spreadsheet_url(spreadsheet_id):
    """
    获取Google Sheet的完整URL
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing"

def send_webhook(sheet_url, sheet_title):
    """
    通过webhook发送Google Sheet链接
    """
    try:
        data = {
            "message": sheet_url,
            "name": sheet_title,
            "timestamp": ""  # 可以添加时间戳
        }
        
        # 发送POST请求
        response = requests.post(WEBHOOK_URL, json=data)
        
        # 检查响应
        print(f"Webhook状态码: {response.status_code}")
        print(f"Webhook响应内容: {response.text}")
        return True
    except Exception as e:
        print(f"发送webhook时发生错误: {e}")
        return False

def upload_csv(csv_path):
    """
    将CSV文件完整备份到同名Google Sheet，设置分享权限并返回链接
    """
    # 获取CSV文件名（不带扩展名）
    sheet_title = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 创建新Sheet
    spreadsheet_id = create(sheet_title)
    
    # 读取CSV内容
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        csv_data = list(csv_reader)
    
    # 构建写入请求
    body = {
        "values": csv_data
    }
    
    # 写入数据
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"更新了 {result.get('updatedCells')} 个单元格")
        
        # 设置分享权限
        share_spreadsheet(spreadsheet_id)
        
        # 获取完整URL
        sheet_url = get_spreadsheet_url(spreadsheet_id)
        print(f"Google Sheet URL: {sheet_url}")
        
        # 发送webhook
        send_webhook(sheet_url, sheet_title)
        
        return sheet_url
    except HttpError as error:
        print(f"写入数据时发生错误: {error}")
        return error

# 在main中调用示例
if __name__ == "__main__":
    csv_file = "news_data_store/test_data/data_250415_raw.csv"  # 替换为你的CSV文件路径
    sheet_url = upload_csv(csv_file)
    print(f"Google Sheet已创建并分享: {sheet_url}")


  # news_data.csv
  # create("mysheettest1")
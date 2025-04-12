import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup

# === 設定 ===
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1rWB5Ohd46mA2T3S1sdFbW11Gzdl1p6DixeHxoiRU_so/edit#gid=0"
linkedin_url = input("請貼上 LinkedIn 職缺分享連結（如：https://www.linkedin.com/jobs/view/4204485955/）:\n")

# === Google Sheets 認證 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url(spreadsheet_url).sheet1

# === 抓取 LinkedIn JD 頁面 ===
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(linkedin_url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# === 擷取資訊 ===
def extract_info(soup):
    try:
        title = soup.find('h1').text.strip()
    except:
        title = "N/A"
    try:
        company = soup.find('a', class_="topcard__org-name-link").text.strip()
    except:
        company = "N/A"
    return title, company

title, company = extract_info(soup)

# === 寫入 Google Sheets ===
sheet.append_row([title, company, linkedin_url])
print("✅ 已成功寫入 Google Sheets！")

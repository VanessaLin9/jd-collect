import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
import json

# === 設定 ===
record_file = Path("record_jobs.json")
print_url = input("請貼上 LinkedIn 職缺分享連結（如：https://www.linkedin.com/jobs/view/4204485955/）:\n").strip()
parsed_url = urlparse(print_url)

# === 判斷平台 ===
def detect_platform(url):
    if "linkedin.com" in url:
        return "linkedin"
    elif "104.com.tw" in url:
        return "104"
    elif "cakeresume.com" in url:
        return "cakeresume"
    return "unknown"

platform = detect_platform(print_url)

# === 抓取 LinkedIn JD 頁面 ===
if platform != "linkedin":
    print("⚠️ 目前只支援 LinkedIn 職缺分享連結")
    exit(1)

# === 解析網址，獲取 currentJobId ===
query_params = parse_qs(parsed_url.query)
job_id = query_params.get('currentJobId', [None])[0]


if not job_id:
    print("⚠️ 沒有抓到 currentJobId，請確認網址正確")
    exit(1)

share_url = f"https://www.linkedin.com/jobs/view/{job_id}/"


headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(share_url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# === 擷取資訊 ===
title_tag = soup.find('title')
title_text = title_tag.text if title_tag else "N/A"
parts = title_text.split(" | ")
job_title = parts[0].strip() if len(parts) > 0 else "N/A"

# === 組成資料項目 ===
job = {
    "platform": platform,
    "title": job_title,
    "share_url": share_url,
    "note_time": datetime.now().isoformat(timespec='seconds')
}

# === 讀取舊資料，新增進去 ===
data = []
if record_file.exists():
    with record_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
else:
    print("⚠️ 找不到紀錄檔，將會創建一個新的紀錄檔。")
    record_file.touch()
    with record_file.open("w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)

# 避免重複（根據 share_url）
if any(j["share_url"] == share_url for j in data):
    print("⚠️ 此職缺已存在於紀錄中，未重複新增。")
else:
    data.append(job)
    with record_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ 已成功記錄：", job)

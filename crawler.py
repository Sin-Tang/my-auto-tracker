import requests
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "rent_history.csv"

API_URL = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&region=3&kind=1&price=10000_20000,20000_30000&layout=3"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def fetch_listings():
    print("🔍 正在從 591 API 抓資料...")
    r = requests.get(API_URL, headers=headers)
    data = r.json()

    houses = data["data"]["data"]
    results = []

    for h in houses:
        results.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "id": h.get("post_id"),
            "title": h.get("title"),
            "address": h.get("community") or "",
            "layout": h.get("layout") or "",
            "price": h.get("price"),
            "link": f"https://rent.591.com.tw/rent/{h.get('post_id')}"
        })

    print(f"📌 共抓到 {len(results)} 筆資料")
    return results


def save_to_csv(data):
    df_new = pd.DataFrame(data)

    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(CSV_FILE, index=False)
    print("📁 CSV 已更新")


def main():
    listings = fetch_listings()
    save_to_csv(listings)
    print("✅ 完成")


if __name__ == "__main__":
    main()

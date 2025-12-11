from playwright.sync_api import sync_playwright
import json
import pandas as pd
import os
from datetime import datetime

CSV_FILE = "rent_history.csv"
SEARCH_URL = "https://rent.591.com.tw/list?region=3&kind=1&price=10000_20000,20000_30000&layout=3"

def fetch_listings():
    print("🚀 使用 Playwright 取得 API JSON...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        listings_json = None

        # 攔截 API 回傳
        def handle_response(response):
            nonlocal listings_json
            if "home/search/rsList" in response.url:
                try:
                    listings_json = response.json()
                except:
                    pass

        page.on("response", handle_response)

        # 開啟網頁觸發 API
        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)  # 給 API 時間回傳 JSON

        browser.close()

        if not listings_json or "data" not in listings_json:
            print("⚠ 無法取得 API JSON，可能被反爬蟲阻擋")
            return []

        houses = listings_json["data"]["data"]
        print(f"📌 取得 {len(houses)} 筆資料")

        results = []
        for h in houses:
            results.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "id": h.get("post_id"),
                "title": h.get("title"),
                "address": h.get("community"),
                "layout": h.get("layout"),
                "price": h.get("price"),
                "link": f"https://rent.591.com.tw/rent/{h.get('post_id')}"
            })

        return results


def save_to_csv(data):
    if not data:
        print("⚠ 沒有資料，不寫入 CSV")
        return

    df_new = pd.DataFrame(data)

    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(CSV_FILE, index=False)
    print("💾 CSV 已更新")


def main():
    listings = fetch_listings()
    save_to_csv(listings)
    print("✅ 完成")


if __name__ == "__main__":
    main()

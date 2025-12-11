from playwright.sync_api import sync_playwright
import requests
import pandas as pd
import os
from datetime import datetime


CSV_FILE = "rent_history.csv"
SEARCH_URL = "https://rent.591.com.tw/list?region=3&kind=1&price=10000_20000,20000_30000&layout=3"
API_URL = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&region=3&kind=1&price=10000_20000,20000_30000&layout=3"


def get_cookies_and_token():
    print("🔍 正在從 Playwright 取得 cookies 與 token ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SEARCH_URL)
        page.wait_for_load_state("networkidle")

        cookies = page.context.cookies()

        token = None
        for c in cookies:
            if c["name"] == "csrf_token":
                token = c["value"]

        browser.close()
        return cookies, token


def fetch_listings():
    cookies, token = get_cookies_and_token()

    if not token:
        print("⚠ 找不到 csrf_token，無法取得 API")
        return []

    jar = requests.cookies.RequestsCookieJar()
    for c in cookies:
        jar.set(c["name"], c["value"], domain=c["domain"])

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-CSRF-TOKEN": token,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": SEARCH_URL,
    }

    print("📡 正在呼叫 591 API ...")
    r = requests.get(API_URL, headers=headers, cookies=jar)

    data = r.json()

    if "data" not in data:
        print("⚠ API 無回傳資料")
        return []

    houses = data["data"]["data"]
    print(f"📌 抓到 {len(houses)} 筆資料")

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
    print("💾 CSV 寫入成功")


def main():
    listings = fetch_listings()
    save_to_csv(listings)


if __name__ == "__main__":
    main()

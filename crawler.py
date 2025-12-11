from playwright.sync_api import sync_playwright
import pandas as pd
import os
from datetime import datetime
import re

SEARCH_URL = "https://rent.591.com.tw/list?region=3&kind=1&price=10000_20000,20000_30000&layout=3"
CSV_FILE = "rent_history.csv"

def extract_id(link):
    match = re.search(r"rent/(\d+)", link)
    return match.group(1) if match else None


def fetch_listings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🔍 正在打開頁面...")
        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        print("🔍 頁面載入完成，開始抓資料...")

        # 找所有房屋卡片
        items = page.query_selector_all(".vue-list-rent-item")
        data = []

        for item in items:
            link_el = item.query_selector("a")
            title_el = item.query_selector(".item-title")
            price_el = item.query_selector(".item-price-text")
            addr_el = item.query_selector(".item-area")
            layout_el = item.query_selector(".item-info .item-info-detail")

            link = link_el.get_attribute("href") if link_el else ""
            title = title_el.inner_text().strip() if title_el else ""
            price = price_el.inner_text().strip() if price_el else ""
            address = addr_el.inner_text().strip() if addr_el else ""
            layout = layout_el.inner_text().strip() if layout_el else ""

            house_id = extract_id(link)

            if house_id:
                data.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "id": house_id,
                    "title": title,
                    "address": address,
                    "layout": layout,
                    "price": price,
                    "link": link
                })

        browser.close()
        print(f"📌 共抓到 {len(data)} 筆資料")
        return data


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
    print("🚀 爬蟲開始執行...")
    listings = fetch_listings()

    if len(listings) == 0:
        print("⚠ 未抓到任何資料，可能是網站更新或選擇器需調整")
        return

    save_to_csv(listings)
    print("✅ 今日資料完成")


if __name__ == "__main__":
    main()

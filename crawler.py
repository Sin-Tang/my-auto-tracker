def fetch_listings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🔍 正在打開頁面...")
        page.goto(SEARCH_URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        print("🔍 頁面載入完成，開始抓資料...")

        # 591 房屋卡片
        items = page.query_selector_all("section.vue-list-rent-item")
        data = []

        for item in items:
            link_el = item.query_selector("a")
            title_el = item.query_selector(".item-title")
            price_el = item.query_selector(".item-price-text")
            addr_el = item.query_selector(".item-area")
            layout_el = item.query_selector(".item-detail-info")

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

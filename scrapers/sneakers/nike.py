import requests

def scrape_nike_air_max_1():
    print("Querying Nike API for Air Max 1 deals...")

    url = "https://api.nike.com/product_feed/threads/v2"
    params = {
        "filter": "marketplace(US)",
        "filter": "language(en)",
        "filter": "searchTerms(air max 1)",
        "anchor": "0",
        "count": "100",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.nike.com",
        "Referer": "https://www.nike.com/",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        products = data.get("objects", [])
        if not products:
            print("No products found.")
            return []

        deals = []
        for product in products:
            product_info = product.get("productInfo", [])
            if not product_info:
                continue

            base = product_info[0]
            title = base.get("productContent", {}).get("fullTitle", "N/A")
            style_color = base.get("merchProduct", {}).get("styleColor", "N/A")
            price_info = base.get("merchPrice", {})
            full_price = price_info.get("fullPrice")
            current_price = price_info.get("currentPrice")
            discount = None
            if full_price and current_price and full_price > current_price:
                discount = round(100 * (full_price - current_price) / full_price)

            deal = {
                "title": title,
                "style_color": style_color,
                "price": current_price,
                "full_price": full_price,
                "discount": discount,
                "url": f"https://www.nike.com/t/{title.replace(' ', '-').lower()}/{style_color}",
            }
            deals.append(deal)

        return deals

    except requests.exceptions.RequestException as e:
        print(f"Failed to query Nike API: {e}")
        return []

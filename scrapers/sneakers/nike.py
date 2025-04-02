import requests


def scrape_nike_air_max_1():
    print("Querying Nike API for Air Max 1 deals...")

    base_url = "https://api.nike.com/product_feed/threads/v2"
    query_string = (
        "filter=marketplace(US)&"
        "filter=language(en)&"
        "filter=searchTerms(air max 1)&"
        "anchor=0&count=100"
    )

    url = f"{base_url}?{query_string}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nike.com/",
        "Origin": "https://www.nike.com",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        products = data.get("objects", [])
        if not products:
            print("No products found.")
            return []

        print(f"Found {len(products)} products.")
        deals = []
        for product in products:
            info = product.get("productInfo", [{}])[0]
            title = info.get("productContent", {}).get("fullTitle", "N/A")
            price_data = info.get("merchPrice", {})
            full_price = price_data.get("fullPrice")
            current_price = price_data.get("currentPrice")
            style_color = info.get("merchProduct", {}).get("styleColor", "N/A")

            if current_price is not None and full_price is not None and current_price < full_price:
                discount = round((full_price - current_price) / full_price * 100)
                deals.append({
                    "title": title,
                    "style": style_color,
                    "price": current_price,
                    "original_price": full_price,
                    "discount": discount,
                })

        return deals

    except requests.exceptions.RequestException as e:
        print(f"Failed to query Nike API: {e}")
        return []

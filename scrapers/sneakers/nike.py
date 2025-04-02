import requests

def scrape_nike_air_max_1():
    print("Querying Nike API for Air Max 1 deals...")

    url = "https://api.nike.com/product_feed/threads/v2"
    params = {
        "filter": [
            "marketplace(US)",
            "language(en)",
            "searchTerms(air max 1)"
        ],
        "anchor": 0,
        "count": 100
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        threads = data.get("objects", [])

        if not threads:
            print("No products returned from Nike API.")
            return []

        results = []
        for product in threads:
            product_info = product.get("publishedContent", {}).get("properties", {})
            title = product_info.get("title", "N/A")
            style_color = product_info.get("styleColor", "N/A")
            price_info = product.get("productInfo", [{}])[0].get("merchPrice", {})
            full_price = price_info.get("fullPrice")
            current_price = price_info.get("currentPrice")
            discount = None
            if full_price and current_price and current_price < full_price:
                discount = round((full_price - current_price) / full_price * 100)

            url_path = product.get("publishedContent", {}).get("properties", {}).get("seo", {}).get("slug", "")
            product_url = f"https://www.nike.com/t/{url_path}/{style_color}"

            results.append({
                "title": title,
                "style_id": style_color,
                "url": product_url,
                "full_price": full_price,
                "current_price": current_price,
                "discount_percent": discount
            })

        return results

    except requests.RequestException as e:
        print(f"Failed to query Nike API: {e}")
        return []

import requests


def scrape_nike_air_max_1():
    print("Querying Nike API for Air Max 1 deals...")

    base_url = "https://api.nike.com/product_feed/threads/v2"
    params = {
        "filter": [
            "marketplace(US)",
            "language(en)",
            "searchTerms(air max 1)"
        ],
        "anchor": 0,
        "count": 100,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("objects"):
            print("No products found.")
            return []

        products = []
        for item in data["objects"]:
            product_info = item.get("productInfo", [{}])[0]

            style_id = product_info.get("merchProduct", {}).get("styleColor")
            title = product_info.get("productContent", {}).get("fullTitle")
            price_info = product_info.get("merchPrice", {})

            full_price = price_info.get("fullPrice")
            sale_price = price_info.get("currentPrice")
            discount = None

            if full_price and sale_price and sale_price < full_price:
                discount = round((1 - sale_price / full_price) * 100)

            products.append({
                "title": title,
                "style_id": style_id,
                "full_price": full_price,
                "sale_price": sale_price,
                "discount": discount,
                "url": f"https://www.nike.com/t/{title.replace(' ', '-').lower()}/{style_id}" if title and style_id else "N/A"
            })

        return products

    except requests.exceptions.RequestException as e:
        print(f"Failed to query Nike API: {e}")
        return []

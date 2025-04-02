import requests

def scrape_nike_air_max_1():
    print("Querying Nike API for Air Max 1 deals...")

    url = "https://api.nike.com/cic/browse/v2"
    params = {
        "query": "air max 1",
        "anchor": 0,
        "count": 100,  # max allowed
        "country": "US",
        "language": "en",
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Failed to query Nike API: {e}")
        return []

    products = data.get("data", {}).get("products", [])
    results = []

    for product in products:
        pid = product.get("id")
        title = product.get("title")
        url = f"https://www.nike.com/t/{product.get('slug')}/{pid}"
        colorways = product.get("colorDescription", "")
        price_info = product.get("price", {})
        full_price = price_info.get("fullPrice")
        current_price = price_info.get("currentPrice")
        is_sale = full_price and current_price and current_price < full_price
        style_color = product.get("styleColor")

        result = {
            "title": title,
            "style_id": style_color,
            "url": url,
            "full_price": full_price,
            "current_price": current_price,
            "is_sale": is_sale,
        }
        results.append(result)

    return results

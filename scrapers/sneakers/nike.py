import requests

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def get_nike_deals():
    """
    Scrapes Nike website for Air Max 1 deals and returns them in a structured format.
    """
    print("🔍 Searching Nike for Air Max 1...")
    deals = {}

    response = requests.get(NIKE_SEARCH_URL)
    
    if response.status_code == 200:
        data = response.json()
        for product in data.get("products", []):
            name = product.get("title")
            price = product.get("price", {}).get("current_price")
            link = product.get("url")
            style_id = product.get("style_color", "UNKNOWN")

            if style_id != "UNKNOWN":
                deals[style_id] = {
                    "name": name,
                    "style_id": style_id,
                    "image": product.get("image_url"),
                    "prices": [{"store": "Nike", "price": price, "link": link}]
                }

        print(f"✅ Found {len(deals)} Nike Air Max 1 deals.")

    else:
        print(f"❌ Failed to fetch Nike deals. Status Code: {response.status_code}")

    return deals

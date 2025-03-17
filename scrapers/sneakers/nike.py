import requests
import time

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def get_nike_deals():
    """
    Scrapes Nike website for Air Max 1 deals and returns them in a structured format.
    """
    print("🔍 Searching Nike for Air Max 1...")
    deals = {}

    try:
        response = requests.get(NIKE_SEARCH_URL, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"❌ Nike request failed! Status Code: {response.status_code}")
            return {}

        try:
            data = response.json()  # Try parsing JSON
        except requests.exceptions.JSONDecodeError:
            print("❌ Error: Nike API did not return valid JSON.")
            print("🔍 Response content (first 500 chars):", response.text[:500])  # Debugging
            return {}

        products = data.get("products", [])

        if not products:
            print("⚠️ No products found on Nike's response. Possible website structure change.")
            return {}

        for product in products:
            name = product.get("title", "Unknown Product")
            price = product.get("price", {}).get("current_price", "N/A")
            link = product.get("url", "#")
            style_id = product.get("style_color", "UNKNOWN")

            if style_id != "UNKNOWN":
                deals[style_id] = {
                    "name": name,
                    "style_id": style_id,
                    "image": product.get("image_url", ""),
                    "prices": [{"store": "Nike", "price": price, "link": f"https://www.nike.com{link}"}]
                }

        print(f"✅ Found {len(deals)} Nike Air Max 1 deals.")
        return deals

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return {}

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {}


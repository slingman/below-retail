import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.footlocker.com"
SEARCH_URL = "https://www.footlocker.com/search?query=air%20max%201"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

def get_footlocker_deals():
    """Scrape Nike Air Max 1 deals from Foot Locker, extracting product style IDs correctly."""
    deals = []
    
    # Step 1: Perform a search request to get the list of products
    response = requests.get(SEARCH_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Error: Failed to fetch Foot Locker search results. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    product_containers = soup.find_all("div", class_="ProductCard")
    
    if not product_containers:
        print("⚠️ Warning: No products found on Foot Locker search page.")
        return []

    for product in product_containers:
        try:
            # Extract product name and URL
            product_name = product.find("p", class_="ProductCard-name").text.strip()
            product_link = product.find("a", class_="ProductCard-link")["href"]
            full_product_url = BASE_URL + product_link

            # Step 2: Visit the product page to extract the style ID (Supplier-SKU)
            style_id = get_footlocker_style_id(full_product_url)
            if not style_id:
                print(f"⚠️ Warning: Missing style_id for {product_name}, skipping.")
                continue  # Skip this product if no style_id is found

            # Extract price
            price_tag = product.find("span", class_="ProductPrice")
            price = float(price_tag.text.replace("$", "").strip()) if price_tag else None

            # Extract image URL
            img_tag = product.find("img", class_="ProductCard-image")
            image_url = img_tag["src"] if img_tag else None

            # Construct deal entry
            deal = {
                "name": product_name,
                "style_id": style_id,
                "image": image_url,
                "prices": [{
                    "store": "Foot Locker",
                    "price": price,
                    "link": full_product_url
                }]
            }
            deals.append(deal)

            # Delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error processing product: {e}")

    return deals


def get_footlocker_style_id(product_url):
    """Extract style ID (Supplier-SKU) from Foot Locker product page."""
    try:
        response = requests.get(product_url, headers=HEADERS)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        style_id_tag = soup.find("span", class_="ProductDetails-sku")
        if style_id_tag:
            return style_id_tag.text.strip()

    except Exception as e:
        print(f"❌ Error fetching style ID from {product_url}: {e}")
    
    return None


# Run scraper when executed directly
if __name__ == "__main__":
    deals = get_footlocker_deals()
    print(deals)

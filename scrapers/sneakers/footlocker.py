import requests
from bs4 import BeautifulSoup

def scrape_footlocker(model):
    print(f"🔍 Searching Foot Locker for {model}...")
    base_url = "https://www.footlocker.com/search?query="
    search_url = f"{base_url}{model.replace(' ', '%20')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch Foot Locker search results for {model}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        deals = {}

        for product in soup.find_all("div", class_="ProductCard"):
            try:
                name = product.find("p", class_="ProductCard-name").text.strip()
                price = product.find("span", class_="ProductPrice").text.strip()
                link = "https://www.footlocker.com" + product.find("a")["href"]
                image = product.find("img")["src"] if product.find("img") else ""

                if model.lower() in name.lower():
                    deals[name] = {
                        "name": name,
                        "image": image,
                        "prices": [{"store": "Foot Locker", "price": price, "link": link}]
                    }
            except:
                continue

        return deals
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Foot Locker search: {e}")
        return {}

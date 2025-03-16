import requests
from bs4 import BeautifulSoup

def scrape_hibbett(model):
    print(f"🔍 Searching Hibbett for {model}...")
    base_url = "https://www.hibbett.com/catalog/search_cmd/"
    search_url = f"{base_url}{model.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch Hibbett search results for {model}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        deals = {}

        for product in soup.find_all("div", class_="product-tile"):
            try:
                name = product.find("div", class_="product-name").text.strip()
                price = product.find("span", class_="sales").text.strip()
                link = "https://www.hibbett.com" + product.find("a")["href"]
                image = product.find("img")["src"] if product.find("img") else ""

                if model.lower() in name.lower():
                    deals[name] = {
                        "name": name,
                        "image": image,
                        "prices": [{"store": "Hibbett", "price": price, "link": link}]
                    }
            except:
                continue

        return deals
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Hibbett search: {e}")
        return {}

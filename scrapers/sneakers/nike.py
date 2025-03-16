import requests
from bs4 import BeautifulSoup

def scrape_nike(model):
    print(f"🔍 Searching Nike for {model}...")
    base_url = "https://www.nike.com/w?q="
    search_url = f"{base_url}{model.replace(' ', '%20')}"  # Format search query
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch Nike search results for {model}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        deals = {}

        for product in soup.find_all("div", class_="product-card"):
            try:
                name = product.find("div", class_="product-card__title").text.strip()
                price = product.find("div", class_="product-price").text.strip()
                link = "https://www.nike.com" + product.find("a")["href"]
                image = product.find("img")["src"] if product.find("img") else ""

                if model.lower() in name.lower():  # Ensure it matches the searched model
                    deals[name] = {
                        "name": name,
                        "image": image,
                        "prices": [{"store": "Nike", "price": price, "link": link}]
                    }
            except:
                continue

        return deals
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Nike search: {e}")
        return {}

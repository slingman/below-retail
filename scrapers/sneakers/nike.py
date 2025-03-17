import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q={query}&vst={query}"

def scrape_nike(sneaker_name):
    search_url = NIKE_SEARCH_URL.format(query=sneaker_name.replace(" ", "%20"))
    driver = get_selenium_driver()
    driver.get(search_url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = []

    for product in soup.find_all("div", class_="product-card"):
        try:
            name = product.find("div", class_="product-card__title").text.strip()
            price = float(product.find("div", class_="product-price").text.replace("$", "").strip())
            link = "https://www.nike.com" + product.find("a")["href"]
            image = product.find("img")["src"] if product.find("img") else ""

            # Extract Style ID from URL
            style_id = link.split("/")[-1] if "/" in link else "Unknown"

            products.append({
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "style_id": style_id
            })
        except:
            continue

    driver.quit()
    return products

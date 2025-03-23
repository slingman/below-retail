import time
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.nike.com"
SEARCH_URL = f"{BASE_URL}/w?q=air%20max%201&vst=air%20max%201"

def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def extract_price(price_text: str) -> str:
    """Cleans the price text by removing the $ symbol and extra whitespace."""
    return price_text.replace("$", "").strip()

def get_product_links(driver: webdriver.Chrome) -> List[str]:
    print("\nFetching Nike deals...")
    driver.get(SEARCH_URL)
    time.sleep(4)
    
    # Attempt to accept cookie consent if present
    try:
        consent_button = driver.find_element(By.ID, "hf_cookie_text_btn_accept")
        consent_button.click()
        print("✅ Accepted cookie consent")
    except Exception:
        print("ℹ️ No cookie consent dialog found")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.find_all("div", class_="product-card")
    print(f"🔎 Found {len(product_cards)} products on Nike search")
    
    product_links = []
    for card in product_cards:
        link = card.find("a", class_="product-card__link-overlay")
        if link and link.get("href") and "/t/" in link["href"]:
            product_links.append(BASE_URL + link["href"])
    product_links = list(set(product_links))
    print(f"Extracted product URLs: {product_links[:25]}")
    return product_links[:10]

def parse_product_page(driver: webdriver.Chrome, url: str) -> Dict:
    driver.get(url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Extract Base Product Name
    product_title_tag = soup.find("h1", {"data-testid": "product_title"})
    base_name = product_title_tag.get_text(strip=True) if product_title_tag else "N/A"
    
    # Extract Base Style ID from description
    style_info = soup.find("li", {"data-testid": "product-description-style-color"})
    style_text = style_info.get_text(strip=True) if style_info else ""
    base_style_id = style_text.replace("Style:", "").strip() if "Style:" in style_text else "N/A"
    
    # Extract Prices (regular and sale if available)
    current_price_tag = soup.find("span", {"data-testid": "currentPrice-container"})
    sale_price = extract_price(current_price_tag.get_text()) if current_price_tag else "N/A"
    
    initial_price_tag = soup.find("span", {"data-testid": "initialPrice-container"})
    full_price = extract_price(initial_price_tag.get_text()) if initial_price_tag else sale_price
    
    # Extract Other Colorway Links
    colorway_links = soup.find_all("a", attrs={"data-testid": re.compile(r"^colorway-link-")})
    other_colorways = []
    for a in colorway_links:
        href = a.get("href")
        if not href:
            continue
        full_url = BASE_URL + href
        match = re.search(r'/([^/]+)$', href)
        colorway_id = match.group(1) if match else "N/A"
        other_colorways.append({
            "url": full_url,
            "style_id": colorway_id
        })
    
    return {
        "site": "Nike",
        "title": base_name,
        "style_id": base_style_id,
        "price": full_price,
        "sale_price": sale_price if full_price != sale_price else None,
        "product_url": url,
        "other_colorways": other_colorways,
    }

def scrape_nike() -> List[Dict]:
    driver = create_driver()
    products = []
    try:
        product_links = get_product_links(driver)
        for idx, url in enumerate(product_links, start=1):
            print(f"\n🔄 Processing Nike product [{idx}]...")
            data = parse_product_page(driver, url)
            print(f"📝 Product Title: {data['title']}")
            print(f"Base Style: {data['style_id']}")
            print(f"Base Price Info: {data['price']}" + (f" (SALE: {data['sale_price']})" if data['sale_price'] else ""))
            products.append(data)
    finally:
        driver.quit()
    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(products)}")
    return products

def get_nike_deals() -> List[Dict]:
    return scrape_nike()

if __name__ == "__main__":
    deals = get_nike_deals()
    for deal in deals:
        print(deal)

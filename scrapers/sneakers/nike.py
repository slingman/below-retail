import time
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.common import extract_price

BASE_URL = "https://www.nike.com"
SEARCH_URL = f"{BASE_URL}/w?q=air%20max%201&vst=air%20max%201"

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_product_links(driver):
    print(f"\nFetching Nike deals...")
    driver.get(SEARCH_URL)
    time.sleep(4)

    try:
        consent_button = driver.find_element(By.ID, "hf_cookie_text_btn_accept")
        consent_button.click()
        print("✅ Accepted cookie dialog")
    except:
        print("ℹ️ No cookie consent dialog found")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.find_all("div", class_="product-card")
    print(f"🔎 Found {len(product_cards)} products on Nike search")

    product_links = []
    for card in product_cards:
        link = card.find("a", class_="product-card__link-overlay")
        if link and "/t/" in link["href"]:
            product_links.append(BASE_URL + link["href"])

    print(f"Extracted product URLs: {product_links[:25]}")
    return product_links[:10]

def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 1. Base Product Name
    product_title = soup.find("h1", {"data-testid": "product_title"})
    base_name = product_title.get_text(strip=True) if product_title else "N/A"

    # 2. Base Product Style ID
    style_info = soup.find("li", {"data-testid": "product-description-style-color"})
    style_text = style_info.get_text(strip=True) if style_info else ""
    style_id = style_text.replace("Style:", "").strip() if "Style:" in style_text else "N/A"

    # 3 & 4. Price / Sale Price
    current_price_tag = soup.find("span", {"data-testid": "currentPrice-container"})
    sale_price = extract_price(current_price_tag.text) if current_price_tag else None

    initial_price_tag = soup.find("span", {"data-testid": "initialPrice-container"})
    full_price = extract_price(initial_price_tag.text) if initial_price_tag else sale_price

    # 5. Other Colorways
    other_colorways = []
    colorway_divs = soup.find_all("a", {"data-testid": re.compile(r"colorway-link-")})
    for div in colorway_divs:
        href = div.get("href")
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
        "style_id": style_id,
        "price": full_price,
        "sale_price": sale_price if full_price != sale_price else None,
        "product_url": url,
        "other_colorways": other_colorways,
    }

def scrape_nike():
    driver = create_driver()
    products = []

    try:
        product_links = get_product_links(driver)
        for idx, url in enumerate(product_links):
            print(f"\n🔄 Processing Nike product [{idx + 1}]...")
            data = parse_product_page(driver, url)
            print(f"📝 Product Title: {data['title']}")
            print(f"Base Style: {data['style_id']}")
            print(f"Base Price Info: {data['price']} {'(SALE: ' + str(data['sale_price']) + ')' if data['sale_price'] else ''}")
            products.append(data)
    finally:
        driver.quit()

    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(products)}")
    return products

def get_nike_deals() -> List[Dict]:
    return scrape_nike()

import time
import re
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASE_URL = "https://www.nike.com"
SEARCH_URL = f"{BASE_URL}/w?q=air%20max%201&vst=air%20max%201"


def extract_price(price_str: str) -> float:
    price_num = re.sub(r"[^\d.]", "", price_str)
    try:
        return float(price_num)
    except ValueError:
        return 0.0


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_product_links(driver: webdriver.Chrome) -> List[str]:
    print("\nFetching Nike deals...")
    driver.get(SEARCH_URL)
    time.sleep(4)

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
            href = link["href"]
            if href.startswith("http"):
                product_links.append(href)
            else:
                product_links.append(BASE_URL + href)

    product_links = list(set(product_links))
    print(f"Extracted product URLs: {product_links[:25]}")
    return product_links[:10]


def parse_product_page(driver: webdriver.Chrome, url: str) -> Dict:
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    title_tag = soup.find("h1", {"data-testid": "product_title"})
    subtitle_tag = soup.find("h2", {"data-testid": "product_subtitle"})
    base_title = title_tag.text.strip() if title_tag else ""
    subtitle = subtitle_tag.text.strip() if subtitle_tag else ""

    description_ul = soup.find("ul", class_=re.compile(".*nds-list.*"))
    base_style_id = ""
    if description_ul:
        for li in description_ul.find_all("li"):
            if "Style:" in li.text:
                base_style_id = li.text.replace("Style:", "").strip()
                break

    price_container = soup.find("div", id="price-container")
    price = sale_price = 0.0
    if price_container:
        price_tag = price_container.find("span", {"data-testid": "currentPrice-container"})
        sale_tag = price_container.find("span", {"data-testid": "initialPrice-container"})
        if price_tag:
            price = extract_price(price_tag.text)
        if sale_tag:
            sale_price = extract_price(sale_tag.text)

    colorways = []
    color_picker = soup.find("div", id="colorway-picker-container")
    if color_picker:
        for a_tag in color_picker.find_all("a", href=True):
            href = a_tag["href"]
            style_id_match = re.search(r"/([A-Z0-9]+-[0-9]{3,})", href)
            if style_id_match:
                color_style_id = style_id_match.group(1)
                color_url = BASE_URL + href if not href.startswith("http") else href

                # Open colorway URL and extract price info
                driver.get(color_url)
                time.sleep(1.5)
                color_soup = BeautifulSoup(driver.page_source, "html.parser")
                color_price = color_sale = 0.0
                color_price_tag = color_soup.find("span", {"data-testid": "currentPrice-container"})
                color_sale_tag = color_soup.find("span", {"data-testid": "initialPrice-container"})
                if color_price_tag:
                    color_price = extract_price(color_price_tag.text)
                if color_sale_tag:
                    color_sale = extract_price(color_sale_tag.text)

                colorways.append({
                    "style_id": color_style_id,
                    "url": color_url,
                    "price": color_price,
                    "sale_price": color_sale
                })

    return {
        "title": base_title,
        "subtitle": subtitle,
        "style_id": base_style_id,
        "price": price,
        "sale_price": sale_price,
        "url": url,
        "colorways": colorways
    }


def scrape_nike() -> List[Dict]:
    driver = create_driver()
    product_links = get_product_links(driver)

    all_deals = []
    for i, url in enumerate(product_links):
        print(f"\n🔄 Processing Nike product [{i+1}]...")
        try:
            data = parse_product_page(driver, url)
            print(f"📝 Product Title: {data['title']}")
            print(f"Base Style: {data['style_id']}")
            print(f"Base Price Info:  ${data['price']} → ${data['sale_price'] if data['sale_price'] else data['price']}")
            print(f"Other Colorways: {len(data['colorways'])} variants")
            all_deals.append(data)
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            continue

    driver.quit()
    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(all_deals)}")
    return all_deals


def get_nike_deals():
    return scrape_nike()

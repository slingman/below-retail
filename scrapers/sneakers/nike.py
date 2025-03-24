import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def extract_price(price_text):
    if not price_text:
        return None
    price_text = price_text.replace('$', '').strip()
    try:
        return float(price_text)
    except ValueError:
        return None


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def accept_cookies(driver):
    try:
        consent = driver.find_element(By.ID, 'hf_cookie_text_cookieAccept')
        consent.click()
        print("✅ Cookie consent accepted")
    except NoSuchElementException:
        print("ℹ️ No cookie consent dialog found")


def get_nike_search_results(driver):
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver.get(search_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_cards = soup.find_all("a", {"data-qa": "product-card-link"})
    product_urls = list({card['href'] for card in product_cards if "href" in card.attrs})
    print(f"🔎 Found {len(product_urls)} products on Nike search")
    return ["https://www.nike.com" + url if url.startswith("/") else url for url in product_urls]


def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(3)
    accept_cookies(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        product_title_elem = soup.find("h1", class_="headline-2")
        product_title = product_title_elem.text.strip() if product_title_elem else "N/A"

        all_styles = {}
        swatches = soup.find_all("li", class_="product-swatch")
        for swatch in swatches:
            style = swatch.get("data-style-color")
            price_elem = swatch.find("span", class_="is--current-price")
            full_price_elem = swatch.find("span", class_="css-1mj6y5p")

            price = extract_price(price_elem.text if price_elem else None)
            full_price = extract_price(full_price_elem.text if full_price_elem else None)

            if style:
                all_styles[style] = {
                    "sale_price": price,
                    "full_price": full_price or price,
                    "url": "https://www.nike.com" + swatch.find("a")["href"] if swatch.find("a") else url,
                }

        base_style_elem = soup.find("div", class_="description-preview__style-color")
        base_style = base_style_elem.text.strip().replace("Style:", "").strip() if base_style_elem else "N/A"

        current_price_elem = soup.select_one("div.css-xq7tty span.is--current-price")
        full_price_elem = soup.select_one("div.css-xq7tty span.css-1mj6y5p")

        current_price = extract_price(current_price_elem.text if current_price_elem else None)
        full_price = extract_price(full_price_elem.text if full_price_elem else None)

        all_styles[base_style] = {
            "sale_price": current_price,
            "full_price": full_price or current_price,
            "url": url
        }

        return {
            "product_title": product_title,
            "base_style": base_style,
            "styles": all_styles
        }

    except Exception as e:
        print(f"❌ Error parsing product page: {url} — {e}")
        return None


def scrape_nike():
    driver = create_driver()
    print("\nFetching Nike deals...")

    try:
        product_urls = get_nike_search_results(driver)
        print("Extracted product URLs:", product_urls[:22])  # Limiting output for readability
        deals = []

        for i, url in enumerate(product_urls[:10]):
            print(f"\n🔄 Processing Nike product [{i+1}]...")
            data = parse_product_page(driver, url)

            if data:
                print(f"📝 Product Title: {data['product_title']}")
                print(f"Base Style: {data['base_style']}")
                for style, price_data in data['styles'].items():
                    sale = price_data['sale_price']
                    full = price_data['full_price']
                    url = price_data['url']
                    if sale and full and sale < full:
                        print(f"💸 Deal → {style}: ${sale} (was ${full}) → {url}")
                    else:
                        print(f"   {style}: ${sale if sale else full} → {url}")

                deals.append(data)

        return deals

    finally:
        driver.quit()


def get_nike_deals():
    return scrape_nike()

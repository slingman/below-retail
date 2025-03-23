import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from utils.common import extract_price


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def accept_cookies(driver):
    try:
        consent_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept All Cookies')]")
        consent_button.click()
        time.sleep(1)
    except NoSuchElementException:
        print("ℹ️ No cookie consent dialog found")


def extract_variant_info(driver):
    try:
        style = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
    except NoSuchElementException:
        style = "N/A"

    try:
        title = driver.find_element(By.CSS_SELECTOR, '[data-test="product-title"]').text.strip()
    except NoSuchElementException:
        title = "N/A"

    try:
        sale_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price-reduced"]')
        sale_price = extract_price(sale_price_elem.text)
    except NoSuchElementException:
        sale_price = None

    try:
        full_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
        full_price = extract_price(full_price_elem.text)
    except NoSuchElementException:
        full_price = None

    return {
        "style_id": style,
        "title": title,
        "price": full_price,
        "sale_price": sale_price
    }


def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(2)

    variant_data = []

    # Accept cookies if shown
    accept_cookies(driver)

    # Check for other colorways
    colorway_links = []
    try:
        colorway_elems = driver.find_elements(By.CSS_SELECTOR, 'a[data-test="product-colorway"]')
        colorway_links = [elem.get_attribute("href") for elem in colorway_elems if elem.get_attribute("href")]
    except NoSuchElementException:
        pass

    all_urls = list(set([url] + colorway_links))

    for link in all_urls:
        driver.get(link)
        time.sleep(2)
        data = extract_variant_info(driver)
        data["url"] = link
        variant_data.append(data)

    return variant_data


def scrape_nike():
    driver = create_driver()
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver.get(search_url)
    time.sleep(3)

    accept_cookies(driver)

    product_links = []
    try:
        product_elements = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        product_links = [elem.get_attribute("href") for elem in product_elements if elem.get_attribute("href")]
        print(f"🔎 Found {len(product_links)} products on Nike search")
    except NoSuchElementException:
        print("❌ No products found on Nike search page")

    # Remove duplicates and only keep Air Max 1
    product_links = list(set(filter(lambda u: "air-max-1" in u.lower(), product_links)))
    print("Extracted product URLs:", product_links)

    results = []

    for idx, url in enumerate(product_links[:10], start=1):  # Limit to 10 for now
        print(f"\n🔄 Processing Nike product [{idx}]...")
        try:
            variants = parse_product_page(driver, url)
            if variants:
                title = variants[0]["title"]
                print(f"📝 Product Title: {title}")
                print(f"Style Variants:")
                for v in variants:
                    price_info = f"${v['sale_price']} → ${v['price']}" if v["sale_price"] else f"${v['price']}"
                    print(f" - {v['style_id']}: {price_info}")
                    v["title"] = title  # unify title
                    results.append(v)
        except Exception as e:
            print(f"❌ Failed to process product at {url}: {e}")

    driver.quit()
    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(results)}\n")
    return results


def get_nike_deals():
    return scrape_nike()

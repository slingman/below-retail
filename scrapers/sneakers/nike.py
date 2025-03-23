import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def extract_colorway_style_id(driver):
    try:
        style_text = driver.find_element(By.XPATH, "//li[contains(text(),'Style:')]").text
        return style_text.replace("Style:", "").strip()
    except NoSuchElementException:
        return None

def extract_prices(driver):
    try:
        price_container = driver.find_element(By.ID, "price-container")
        prices = price_container.find_elements(By.XPATH, ".//span[contains(@data-testid, 'Price')]")
        price = sale_price = None
        if len(prices) == 1:
            price = prices[0].text.strip()
        elif len(prices) > 1:
            sale_price = prices[0].text.strip()
            price = prices[1].text.strip()
        return price, sale_price
    except NoSuchElementException:
        return None, None

def extract_product_title(driver):
    try:
        return driver.find_element(By.XPATH, "//h1[@data-testid='product_title']").text.strip()
    except NoSuchElementException:
        return None

def extract_colorways(driver):
    colorways = []
    try:
        colorway_links = driver.find_elements(By.XPATH, "//a[contains(@data-testid, 'colorway-link-')]")
        for link in colorway_links:
            href = link.get_attribute("href")
            if href:
                colorways.append(href)
    except NoSuchElementException:
        pass
    return list(set(colorways))

def scrape_nike():
    driver = create_driver()
    base_search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    print("\nFetching Nike deals...")
    driver.get(base_search_url)

    # Handle cookie banner if present
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "gen-nav-commerce-cookie-banner-accept-button"))).click()
        print("✅ Accepted cookie consent")
    except TimeoutException:
        print("ℹ️ No cookie consent dialog found")

    time.sleep(3)

    product_links = []
    product_cards = driver.find_elements(By.XPATH, "//a[@data-testid='product-card__link-overlay']")
    print(f"🔎 Found {len(product_cards)} products on Nike search")
    for card in product_cards:
        href = card.get_attribute("href")
        if href and href.startswith("https://www.nike.com/t/"):
            product_links.append(href)

    product_links = list(set(product_links))
    print(f"Extracted product URLs: {product_links[:25]}")

    all_deals = []
    for idx, url in enumerate(product_links[:10]):
        print(f"\n🔄 Processing Nike product [{idx+1}]...")
        driver.get(url)
        time.sleep(2)

        base_product_name = extract_product_title(driver)
        base_style_id = extract_colorway_style_id(driver)
        base_price, base_sale_price = extract_prices(driver)

        print(f"📝 Product Title: {base_product_name}")
        print(f"Base Style: {base_style_id}")
        print(f"Base Price Info: {base_price} {'| Sale: ' + base_sale_price if base_sale_price else ''}")

        all_colorways = extract_colorways(driver)
        colorway_deals = []

        for cw_url in all_colorways:
            driver.get(cw_url)
            time.sleep(1.5)
            style_id = extract_colorway_style_id(driver)
            price, sale_price = extract_prices(driver)
            colorway_deals.append({
                "url": cw_url,
                "style_id": style_id,
                "price": price,
                "sale_price": sale_price
            })

        all_deals.append({
            "product_name": base_product_name,
            "style_id": base_style_id,
            "price": base_price,
            "sale_price": base_sale_price,
            "url": url,
            "colorways": colorway_deals
        })

    driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(all_deals)}")
    return all_deals

def get_nike_deals():
    return scrape_nike()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

def get_footlocker_deals():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("chromedriver")  # Adjust this if needed
    driver = webdriver.Chrome(service=service, options=options)

    base_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    print(f"\n🔍 Scraping Foot Locker: {base_url}")

    driver.get(base_url)
    time.sleep(3)  # Allow page to load

    deals = []
    product_links = set()

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "a.ProductCard-link")
        for product in products:
            link = product.get_attribute("href")
            if link:
                product_links.add(link)

    except NoSuchElementException:
        print("⚠️ No product links found on the search page.")

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(2)  # Allow page to load
            
            # Extract Product Name
            try:
                product_name = driver.find_element(By.CSS_SELECTOR, "h1.ProductName-primary").text.strip()
            except NoSuchElementException:
                print(f"⚠️ Product name not found for {link}")
                continue

            # Extract Price
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, "span.ProductPrice")
                price = price_element.text.strip()
            except NoSuchElementException:
                print(f"⚠️ Price not found for {link}")
                price = "Price not found"

            # Extract Supplier SKU (Matches Nike's Style ID)
            try:
                supplier_sku_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Supplier-sku #')]")
                supplier_sku = supplier_sku_element.text.split("#")[-1].strip()
            except NoSuchElementException:
                print(f"⚠️ Supplier SKU not found for {link}")
                supplier_sku = "N/A"

            deals.append({
                "name": product_name,
                "price_final": price,
                "link": link,
                "supplier_sku": supplier_sku  # Matches Nike's style ID
            })

        except Exception as e:
            print(f"⚠️ Error processing product: {link}, Message: {e}")

    driver.quit()
    return deals

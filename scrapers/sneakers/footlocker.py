from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_footlocker_deals():
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://www.footlocker.com"
    search_url = f"{base_url}/search?query=nike%20air%20max%201"

    print(f"🔍 Scraping Foot Locker: {search_url}")
    driver.get(search_url)
    time.sleep(5)  # Let the page load

    products = []
    
    # Get all product links from search results
    product_elements = driver.find_elements(By.CSS_SELECTOR, ".ProductCard-link")
    product_links = [elem.get_attribute("href") for elem in product_elements]

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(3)  # Wait for the product page to load
            
            name = driver.find_element(By.CSS_SELECTOR, "h1.ProductName-primary").text
            
            # **Extract the correct style ID (Supplier-sku #)**
            try:
                supplier_sku = driver.find_element(By.XPATH, "//span[contains(text(), 'Supplier-sku #')]/following-sibling::span").text
            except:
                supplier_sku = "Unknown"

            try:
                price_final = driver.find_element(By.CSS_SELECTOR, ".ProductPrice-final").text
            except:
                price_final = "Price not found"

            try:
                price_original = driver.find_element(By.CSS_SELECTOR, ".ProductPrice-original").text
            except:
                price_original = price_final  # If no original price, use final price

            product = {
                "name": name,
                "supplier_sku": supplier_sku,  # ✅ Use the correct style ID for matching
                "price_final": price_final,
                "price_original": price_original,
                "link": link,
            }
            products.append(product)
            print(product)
        
        except Exception as e:
            print(f"⚠️ Error processing product: {link}, {e}")
            continue

    driver.quit()
    return products

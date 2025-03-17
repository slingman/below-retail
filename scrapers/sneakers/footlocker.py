from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_footlocker_deals():
    """Fetches Nike Air Max 1 deals from Foot Locker and extracts supplier SKU for price comparison."""
    
    base_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use webdriver-manager to handle ChromeDriver installation
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print(f"\n🔍 Scraping Foot Locker: {base_url}")
        driver.get(base_url)
        time.sleep(3)

        deals = []
        products = driver.find_elements(By.CSS_SELECTOR, "div.ProductCard")

        for product in products:
            try:
                link_element = product.find_element(By.CSS_SELECTOR, "a.ProductCard-link")
                product_url = link_element.get_attribute("href")
                product_name = product.find_element(By.CSS_SELECTOR, "span.ProductName-primary").text
                price = product.find_element(By.CSS_SELECTOR, "span.ProductPrice").text

                # Navigate to product page to extract supplier SKU (which matches Nike's style ID)
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(product_url)
                time.sleep(2)

                try:
                    supplier_sku = driver.find_element(By.XPATH, "//div[contains(text(),'Supplier-sku #')]/following-sibling::div").text
                except:
                    supplier_sku = "N/A"

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                deals.append({
                    "name": product_name,
                    "price_final": price,
                    "link": product_url,
                    "supplier_sku": supplier_sku
                })

            except Exception as e:
                print(f"⚠️ Error processing product: {product_url}, Message: {str(e)}")
        
        return deals

    finally:
        driver.quit()

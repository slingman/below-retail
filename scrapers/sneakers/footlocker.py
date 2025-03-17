from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time

BASE_URL = "https://www.footlocker.com"

def get_footlocker_deals():
    """Scrape Nike Air Max 1 deals from Foot Locker, ensuring correct style ID matching."""
    
    options = Options()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Ensure correct Chrome binary path
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    deals = []
    search_url = f"{BASE_URL}/search?query=nike%20air%20max%201"
    driver.get(search_url)
    time.sleep(3)  # Allow page to load

    products = driver.find_elements("css selector", ".ProductCard")
    
    for product in products:
        try:
            link_element = product.find_element("css selector", "a.ProductCard-link")
            product_link = link_element.get_attribute("href")

            driver.get(product_link)
            time.sleep(2)  # Allow product page to load

            try:
                name = driver.find_element("css selector", "h1.ProductName-primary").text
                price = driver.find_element("css selector", ".ProductPrice").text
            except NoSuchElementException:
                print(f"⚠️ Price or Name not found for {product_link}")
                price = "Price not found"
                name = "Nike Air Max 1"

            try:
                supplier_sku = driver.find_element("css selector", "[data-test='supplier-sku']").text  # Ensure correct element
            except NoSuchElementException:
                print(f"⚠️ Supplier SKU not found for {product_link}")
                supplier_sku = None

            deals.append({
                "name": name,
                "price_final": price,
                "link": product_link,
                "style_id": supplier_sku  # Ensure this matches Nike's format
            })

        except Exception as e:
            print(f"⚠️ Error processing product: {product_link}, Message: {e}")

    driver.quit()
    return deals

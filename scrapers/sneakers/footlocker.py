import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Selenium WebDriver
def get_driver():
    options = Options()
    options.add_argument("--headless")  # Run without UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())  # Automatically download correct ChromeDriver
    return webdriver.Chrome(service=service, options=options)

def get_footlocker_deals():
    driver = get_driver()
    base_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    print(f"\n🔍 Scraping Foot Locker: {base_url}")
    
    driver.get(base_url)
    time.sleep(5)  # Allow page to load

    deals = []
    product_links = driver.find_elements(By.CSS_SELECTOR, "a.ProductCard-link")
    
    for link in product_links[:15]:  # Limit to first 15 products for speed
        product_url = link.get_attribute("href")
        if product_url:
            try:
                deals.append(scrape_footlocker_product(driver, product_url))
            except Exception as e:
                print(f"⚠️ Error processing product: {product_url}, Message: {e}")
    
    driver.quit()
    return [deal for deal in deals if deal]  # Filter out None values

def scrape_footlocker_product(driver, url):
    """Scrape individual Foot Locker product page"""
    print(f"🔗 Visiting {url}")
    driver.get(url)
    time.sleep(3)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1.ProductName-primary").text.strip()
    except:
        name = "Unknown"

    try:
        price = driver.find_element(By.CSS_SELECTOR, ".ProductPrice-final").text.strip()
    except:
        price = "Price not found"

    try:
        supplier_sku = driver.find_element(By.XPATH, "//div[contains(text(),'Supplier-sku')]/following-sibling::div").text.strip()
    except:
        supplier_sku = "Unknown"

    return {
        "name": name,
        "price_final": price,
        "link": url,
        "supplier_sku": supplier_sku  # This now correctly matches Nike’s "Style ID"
    }


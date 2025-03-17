from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

def get_footlocker_deals():
    driver = get_driver()
    search_url = "https://www.footlocker.com/search?query=air%20max%201"  # Corrected URL
    driver.get(search_url)

    deals = []
    try:
        # Wait until products are visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ProductCard"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductCard")

        for product in products:
            retry_attempts = 3  # Retry mechanism for stale elements
            while retry_attempts > 0:
                try:
                    name_element = product.find_element(By.CSS_SELECTOR, "a.ProductCard-link")
                    price_element = product.find_element(By.CSS_SELECTOR, "div.ProductCard-price")

                    name = name_element.text.strip()
                    price_text = price_element.text.replace("$", "").strip()
                    price = float(price_text) if price_text else None  # Handle missing prices

                    link = name_element.get_attribute("href")
                    
                    deals.append({
                        "store": "Foot Locker",
                        "name": name,
                        "price": price,
                        "link": f"https://www.footlocker.com{link}"  # Ensure full URL
                    })
                    break  # Break out of retry loop on success
                except StaleElementReferenceException:
                    retry_attempts -= 1
                    print("🔄 Retrying stale element...")

    except TimeoutException:
        print("❌ Timeout: No products found on Foot Locker for 'Air Max 1'")
    
    driver.quit()
    return deals

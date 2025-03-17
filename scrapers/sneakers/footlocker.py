from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_footlocker_deals():
    url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for page to load

        deals = []
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product Name
                try:
                    product_name = card.find_element(By.CLASS_NAME, "ProductCard-title").text
                except:
                    product_name = card.find_element(By.CLASS_NAME, "ProductName-primary").text  

                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")

                # Extract Image URL
                try:
                    image_url = card.find_element(By.CLASS_NAME, "ProductCard-image--primary").get_attribute("src")
                except:
                    image_url = None  

                # Extract Prices
                try:
                    sale_price = card.find_element(By.CLASS_NAME, "ProductCard-pricing__sale").text
                    sale_price = float(sale_price.replace("$", ""))  
                except:
                    sale_price = None

                try:
                    original_price = card.find_element(By.CLASS_NAME, "ProductCard-pricing__regular").text
                    original_price = float(original_price.replace("$", ""))  
                except:
                    original_price = sale_price  

                # Ensure at least one valid price is present
                if not sale_price and not original_price:
                    continue  

                # Extract Product ID (this is **not** the Nike style ID)
                product_id = product_url.split("/")[-1].split(".")[0]  

                # Extract Style ID from product page (Matching Nike's style ID)
                driver.get(product_url)
                time.sleep(2)  
                try:
                    style_id = driver.find_element(By.XPATH, "//span[contains(text(), 'Supplier-sku #')]/following-sibling::span").text.strip()
                except:
                    style_id = None  

                # Store deal information
                deals.append({
                    "store": "Foot Locker",
                    "name": product_name,  
                    "url": product_url,    
                    "image": image_url,    
                    "price": sale_price if sale_price else original_price,  
                    "original_price": original_price,
                    "product_id": product_id,  
                    "style_id": style_id  
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

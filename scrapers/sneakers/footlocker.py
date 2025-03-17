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
                # Extract Product Name (try different possible class names)
                try:
                    product_name = card.find_element(By.CLASS_NAME, "ProductCard-title").text
                except:
                    product_name = card.find_element(By.CLASS_NAME, "ProductName-primary").text  # Fallback
                
                if not product_name:
                    product_name = "Unknown Product"  # Ensure a name is always present
                
                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")

                # Extract Image URL
                try:
                    image_url = card.find_element(By.CLASS_NAME, "ProductCard-image--primary").get_attribute("src")
                except:
                    image_url = None  # Allow for cases where no image is found

                # Extract Prices
                try:
                    sale_price = card.find_element(By.CLASS_NAME, "ProductCard-pricing__sale").text
                except:
                    sale_price = None

                try:
                    original_price = card.find_element(By.CLASS_NAME, "ProductCard-pricing__regular").text
                except:
                    original_price = sale_price  # If no original price, assume no discount

                # Ensure at least one valid price is present
                if not sale_price and not original_price:
                    continue  # Skip products with no price

                # Extract Style ID (if available)
                try:
                    style_id = product_url.split("/")[-1].split(".")[0]  # Extract last part of URL before ".html"
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
                    "style_id": style_id,  
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

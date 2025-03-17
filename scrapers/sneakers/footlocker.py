from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def clean_price(price_text):
    """ Remove non-numeric characters and convert price to float. """
    if price_text:
        return float(re.sub(r"[^\d.]", "", price_text))
    return None

def extract_supplier_sku(product_url, driver):
    """ Opens the product page and extracts Supplier-SKU (Nike’s Style ID). """
    try:
        driver.get(product_url)
        time.sleep(3)  # Give page time to load

        # Look for Supplier-SKU (ensure it's case-insensitive & allows spaces)
        try:
            sku_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Supplier-sku #:')]/following-sibling::span")
            supplier_sku = sku_element.text.strip()
            return supplier_sku
        except:
            print(f"⚠️ Supplier-SKU not found on {product_url}")
            return None  # Skip if Supplier-SKU not found

    except Exception as e:
        print(f"⚠️ Error extracting Supplier-SKU from {product_url}: {e}")
        return None

def get_footlocker_deals():
    url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
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
                    product_name = card.find_element(By.CLASS_NAME, "ProductName-primary").text  # Fallback
                
                if not product_name:
                    continue  # Skip if name is missing
                
                if "Air Max 1" not in product_name:
                    continue  # Skip non-Air Max 1 products

                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")

                # Extract Image URL
                try:
                    image_url = card.find_element(By.CLASS_NAME, "ProductCard-image--primary").get_attribute("src")
                except:
                    image_url = None  

                # Extract Prices
                try:
                    sale_price = clean_price(card.find_element(By.CLASS_NAME, "ProductCard-pricing__sale").text)
                except:
                    sale_price = None

                try:
                    original_price = clean_price(card.find_element(By.CLASS_NAME, "ProductCard-pricing__regular").text)
                except:
                    original_price = sale_price  

                if not sale_price and not original_price:
                    continue  # Skip products with no price

                # Extract Style ID from Supplier-SKU on Product Page
                style_id = extract_supplier_sku(product_url, driver)

                # Ensure the `style_id` is extracted and stored
                if not style_id:
                    print(f"⚠️ No style ID found for {product_name}, skipping...")
                    continue  # Skip products where we can't match to Nike

                # Store deal information
                deals.append({
                    "store": "Foot Locker",
                    "name": product_name,  
                    "url": product_url,    
                    "image": image_url,    
                    "price": sale_price if sale_price else original_price,  
                    "original_price": original_price,
                    "style_id": style_id,  # This should now match Nike's Style ID
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

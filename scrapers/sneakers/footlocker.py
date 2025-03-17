from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(search_url)
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
                    product_name = "Unknown Product"  # Ensure a name is always present
                
                # Extract Raw Product URL
                try:
                    raw_product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                except:
                    raw_product_url = None

                # Extract the Foot Locker Product # from the URL
                footlocker_product_id = None
                if raw_product_url:
                    match = re.search(r"/([^/]+)\.html", raw_product_url)
                    if match:
                        footlocker_product_id = match.group(1)

                # Construct the correct Foot Locker product page URL
                if footlocker_product_id:
                    product_url = f"https://www.footlocker.com/product/~/{footlocker_product_id}.html"
                else:
                    product_url = raw_product_url  # Fallback if extraction fails

                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

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

                # Visit the product page to extract the "Supplier-sku #" (Nike's Style ID)
                driver.get(product_url)
                time.sleep(5)  # Allow time for the product page to load (increased wait time)

                # DEBUG: Print full product page content to see if "Supplier-sku #" exists
                full_page_text = driver.page_source
                print("\nDEBUG: Full product page HTML from Foot Locker:\n", full_page_text[:2000])  # Print first 2000 characters

                # First attempt: Regular expression to find "Supplier-sku #"
                try:
                    match = re.search(r"Supplier-sku\s*#:\s*([\w-]+)", full_page_text)
                    if match:
                        style_id = match.group(1).strip()
                        print(f"✅ Foot Locker Style ID Extracted (Supplier-sku #): {style_id}")
                    else:
                        style_id = None
                        print(f"⚠️ Foot Locker Style ID Not Found via text scan.")

                except Exception as e:
                    style_id = None
                    print(f"⚠️ Error extracting Foot Locker Style ID: {e}")

                # Second attempt: Search for JSON metadata in the page
                if style_id is None:
                    try:
                        json_match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});', full_page_text, re.DOTALL)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            style_id = json_data.get('product', {}).get('supplierSku', None)
                            if style_id:
                                print(f"✅ Extracted Style ID from JSON: {style_id}")
                    except Exception as e:
                        print(f"⚠️ Error extracting Supplier-sku # from JSON: {e}")

                # Store deal information
                deals.append({
                    "store": "Foot Locker",
                    "product_name": product_name,  
                    "product_url": product_url,    
                    "image_url": image_url,    
                    "price": sale_price if sale_price else original_price,  
                    "original_price": original_price,
                    "style_id": style_id,  # Supplier-sku # is Nike's Style ID
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

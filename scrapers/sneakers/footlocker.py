from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_footlocker_deals():
    url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up Selenium WebDriver (keeping your setup unchanged)
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
                # Extract Product Name (handling variations in class names)
                try:
                    product_name = card.find_element(By.CLASS_NAME, "ProductName-primary").text
                except:
                    product_name = card.find_element(By.CLASS_NAME, "ProductCard-title").text

                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")

                # Extract Image URL (handling different possible class names)
                try:
                    image_url = card.find_element(By.CLASS_NAME, "ProductCard-image--primary").get_attribute("src")
                except:
                    image_url = card.find_element(By.TAG_NAME, "img").get_attribute("src")

                # Extract Prices (handling changes in pricing structure)
                try:
                    sale_price = card.find_element(By.CLASS_NAME, "ProductPrice-sale").text
                except:
                    sale_price = None

                try:
                    original_price = card.find_element(By.CLASS_NAME, "ProductPrice-original").text
                except:
                    original_price = sale_price  # If no original price, assume no discount

                # Extract Style ID (ensuring it remains valid)
                try:
                    style_id = product_url.split("/")[-1].split(".")[0]  # Extract last part of URL before ".html"
                except:
                    style_id = None

                # Store deal information
                deals.append({
                    "store": "Foot Locker",
                    "product_name": product_name,
                    "product_url": product_url,
                    "image_url": image_url,
                    "sale_price": sale_price,
                    "original_price": original_price,
                    "style_id": style_id,  # Ensures Nike & Foot Locker match
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

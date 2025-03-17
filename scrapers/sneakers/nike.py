from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_nike_deals():
    url = "https://www.nike.com/w?q=air+max+1"

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
        product_cards = driver.find_elements(By.CLASS_NAME, "product-card")

        for card in product_cards:
            try:
                # Extract Product Name with a fallback
                try:
                    product_name = card.find_element(By.CLASS_NAME, "product-card__title").text
                except:
                    product_name = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__title']").text

                # Extract Product URL
                try:
                    product_url = card.find_element(By.CLASS_NAME, "product-card__link-overlay").get_attribute("href")
                except:
                    product_url = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__link-overlay']").get_attribute("href")

                # Extract Style ID from URL
                style_id = product_url.split("/")[-1]  # Get last part of URL (e.g., FZ5808-400)
                print(f"✅ Nike Style ID Extracted: {style_id}")  # Debugging print

                # Extract Image URL
                try:
                    image_url = card.find_element(By.CLASS_NAME, "product-card__hero-image").get_attribute("src")
                except:
                    image_url = card.find_element(By.CSS_SELECTOR, "img.product-card__hero-image").get_attribute("src")

                # Extract Prices with fallbacks
                try:
                    sale_price_element = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price-reduced']")
                    sale_price = sale_price_element.text.replace("$", "").strip()
                except:
                    sale_price = None

                try:
                    original_price_element = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price']")
                    original_price = original_price_element.text.replace("$", "").strip()
                except:
                    original_price = sale_price  # If no original price, assume no discount

                # Ensure price is properly formatted
                try:
                    sale_price = float(sale_price) if sale_price else None
                    original_price = float(original_price) if original_price else None
                except:
                    sale_price, original_price = None, None

                print(f"🟢 Nike Product Found: {product_name} | Price: {sale_price} | Style ID: {style_id}")

                # Store deal information
                deals.append({
                    "store": "Nike",
                    "product_name": product_name,
                    "product_url": product_url,
                    "image_url": image_url,
                    "sale_price": sale_price,
                    "original_price": original_price,
                    "style_id": style_id,
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

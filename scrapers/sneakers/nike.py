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
                # Extract Product Name
                product_name = card.find_element(By.CLASS_NAME, "product-card__title").text

                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "product-card__link-overlay").get_attribute("href")

                # Extract Style ID from URL
                style_id = product_url.split("/")[-1]  # Get last part of URL (e.g., FZ5808-400)

                # Extract Image URL
                image_url = card.find_element(By.CLASS_NAME, "product-card__hero-image").get_attribute("src")

                # Extract Prices
                try:
                    sale_price = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price-reduced']").text
                except:
                    sale_price = None

                try:
                    original_price = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price']").text
                except:
                    original_price = sale_price  # If no original price, assume no discount

                # Store deal information
                deals.append({
                    "store": "Nike",
                    "product_name": product_name,
                    "product_url": product_url,
                    "image_url": image_url,
                    "sale_price": sale_price,
                    "original_price": original_price,
                    "style_id": style_id,  # Added style_id to fix KeyError
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

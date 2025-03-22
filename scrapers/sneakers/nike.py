from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

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

    deals = []

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the search results page to load

        # Find product cards on the search results page
        product_cards = driver.find_elements(By.CLASS_NAME, "product-card")
        if not product_cards:
            print("⚠️ No products found on Nike.")
            return deals

        # Process each product card (you can adjust the number of products processed)
        for card in product_cards:
            try:
                # Extract product title
                try:
                    product_name = card.find_element(By.CLASS_NAME, "product-card__title").text
                except:
                    product_name = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__title']").text

                # Extract product URL from the card
                try:
                    product_url = card.find_element(By.CLASS_NAME, "product-card__link-overlay").get_attribute("href")
                except:
                    product_url = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__link-overlay']").get_attribute("href")

                # Use the URL’s final segment as the base style id
                base_style_id = product_url.split("/")[-1]

                # Extract image URL and prices from the card
                try:
                    image_url = card.find_element(By.CLASS_NAME, "product-card__hero-image").get_attribute("src")
                except:
                    image_url = card.find_element(By.CSS_SELECTOR, "img.product-card__hero-image").get_attribute("src")
                try:
                    sale_price = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price-reduced']").text
                except:
                    sale_price = None
                try:
                    original_price = card.find_element(By.CSS_SELECTOR, "div[data-testid='product-price']").text
                except:
                    original_price = sale_price

                print(f"Processing Nike product: {product_name} | Base Style ID: {base_style_id}")

                # Visit the product page to handle colorways
                driver.get(product_url)
                time.sleep(5)  # Allow the product page to load

                colorway_data = []
                try:
                    # Look for the colorway picker container by its ID
                    colorway_container = driver.find_element(By.ID, "colorway-picker-container")
                    # Extract all colorway links (the <a> elements with a data-testid starting with "colorway-link-")
                    colorway_links = colorway_container.find_elements(By.XPATH, ".//a[starts-with(@data-testid, 'colorway-link-')]")
                    print(f"Found {len(colorway_links)} colorways for product: {product_name}")
                    for link in colorway_links:
                        # Get the href from each colorway link
                        colorway_href = link.get_attribute("href")
                        # The style ID is assumed to be the last segment of the href
                        colorway_style_id = colorway_href.split("/")[-1]
                        colorway_data.append({
                            "colorway_href": colorway_href,
                            "style_id": colorway_style_id
                        })
                except Exception as e:
                    print(f"No colorway picker found for product {product_name}, using default style id. Error: {e}")
                    colorway_data.append({
                        "colorway_href": product_url,
                        "style_id": base_style_id
                    })

                # Create an entry for each colorway found
                for cw in colorway_data:
                    deals.append({
                        "store": "Nike",
                        "product_name": product_name,
                        "product_url": cw["colorway_href"],
                        "image_url": image_url,
                        "sale_price": sale_price,
                        "original_price": original_price,
                        "style_id": cw["style_id"]
                    })
                    print(f"Stored Nike deal: {product_name} | Style ID: {cw['style_id']} | URL: {cw['colorway_href']}")

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

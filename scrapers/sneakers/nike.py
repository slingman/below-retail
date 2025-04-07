import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.selenium_setup import create_webdriver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = create_webdriver(headless=False)  # Open browser window for debugging

    try:
        print("Finding product links...")
        driver.get(NIKE_SEARCH_URL)
        time.sleep(3)  # Give time for page content to load

        product_links = []
        cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        for card in cards:
            href = card.get_attribute('href')
            if href and href.startswith("https://www.nike.com/t/air-max-1"):
                product_links.append(href)

        print(f"Found {len(product_links)} product links.")

        deals = []
        for idx, link in enumerate(product_links[:5]):  # TEMP LIMIT: Only process first 5 for stability
            try:
                print(f"\nScraping product {idx + 1}: {link}")
                driver.get(link)
                time.sleep(2)

                title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text
                try:
                    style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text
                except:
                    style = "N/A"

                try:
                    price = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']").text
                except:
                    price = "N/A"

                print(f"✓ {title} | {style} | {price}")
                deals.append({
                    "title": title,
                    "style_id": style,
                    "price": price,
                    "url": link
                })
                time.sleep(2)  # short pause between requests
            except Exception as e:
                print(f"Failed to scrape {link} due to error: {type(e).__name__}: {e}")
                continue

        return deals
    finally:
        driver.quit()

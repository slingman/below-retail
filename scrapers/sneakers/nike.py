import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from utils.selenium_setup import get_selenium_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def get_nike_deals():
    """
    Scrapes Nike's website for Air Max 1 deals using Selenium.
    """
    print("🔍 Searching Nike for Air Max 1...")
    deals = {}

    # Set up Selenium driver
    driver = get_selenium_driver(headless=True)  # Headless mode for speed

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(5)  # Let the page load

        products = driver.find_elements(By.CLASS_NAME, "product-card__body")

        if not products:
            print("⚠️ No products found. Nike may have changed its layout.")
            return {}

        for product in products:
            try:
                name = product.find_element(By.CLASS_NAME, "product-card__title").text
                price = product.find_element(By.CLASS_NAME, "product-price").text.replace("$", "").strip()
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")

                # Extract Style ID from URL
                style_id = link.split("/")[-1] if "/" in link else "UNKNOWN"

                if style_id != "UNKNOWN":
                    deals[style_id] = {
                        "name": name,
                        "style_id": style_id,
                        "image": "",  # Placeholder (Nike requires dynamic image extraction)
                        "prices": [{"store": "Nike", "price": float(price), "link": link}]
                    }

            except Exception as e:
                print(f"⚠️ Error processing product: {e}")

        print(f"✅ Found {len(deals)} Nike Air Max 1 deals.")
        return deals

    except Exception as e:
        print(f"❌ Nike Scraper Error: {e}")
        return {}

    finally:
        driver.quit()  # Close Selenium driver

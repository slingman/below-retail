import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.selenium_setup import create_webdriver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    print("Finding product links...")

    driver = create_webdriver(headless=False)  # Headless OFF for debugging
    driver.get(NIKE_SEARCH_URL)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__link-overlay"))
        )
        product_links = list({
            a.get_attribute("href") for a in driver.find_elements(By.CLASS_NAME, "product-card__link-overlay")
        })
        print(f"Found {len(product_links)} product links.\n")
    except Exception as e:
        print(f"Failed to extract product links: {e}")
        driver.quit()
        return []

    all_deals = []

    for link in product_links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "description-preview__style-color"))
            )

            title_elem = driver.find_element(By.CLASS_NAME, "headline-2")
            title = title_elem.text.strip()

            style_elem = driver.find_element(By.CLASS_NAME, "description-preview__style-color")
            style = style_elem.text.strip().split(" ")[-1]

            try:
                sale_price_elem = driver.find_element(By.CLASS_NAME, "product-price__highlight")
                sale_price = sale_price_elem.text.strip()
                original_price = driver.find_element(By.CLASS_NAME, "product-price__msrp").text.strip()
            except:
                sale_price = None
                original_price = driver.find_element(By.CLASS_NAME, "product-price").text.strip()

            deal = {
                "title": title,
                "url": link,
                "style": style,
                "original_price": original_price,
                "sale_price": sale_price,
            }
            all_deals.append(deal)

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")

    driver.quit()
    return all_deals

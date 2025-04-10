# scrapers/sneakers/nike.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException
)
from utils.selenium_setup import create_webdriver
import time


def scrape_nike_air_max_1():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()
    wait = WebDriverWait(driver, 10)
    deals = []

    print("Finding product links...")
    driver.get(search_url)
    time.sleep(3)

    product_cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
    product_links = list({card.get_attribute('href') for card in product_cards})
    print(f"Found {len(product_links)} product links.\n")

    for idx, link in enumerate(product_links, 1):
        print(f"Scraping product {idx}: {link}")
        try:
            driver.get(link)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1#pdp_product_title")))
            time.sleep(1)

            swatches = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="colorway-link-"]')
            variant_links = [link.get_attribute("href") for link in swatches]

            # include base page as well
            if link not in variant_links:
                variant_links.insert(0, link)

            for variant_url in variant_links:
                try:
                    driver.get(variant_url)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1#pdp_product_title")))
                    time.sleep(1)

                    title = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text.strip()
                    style = "Unknown Style"
                    try:
                        style = driver.find_element(By.XPATH, "//li[contains(text(), 'Style:')]").text.split("Style:")[1].strip()
                    except NoSuchElementException:
                        pass

                    current_price_elem = driver.find_elements(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]')
                    original_price_elem = driver.find_elements(By.CSS_SELECTOR, '[data-testid="initialPrice-container"]')

                    current_price = current_price_elem[0].text.strip() if current_price_elem else "N/A"
                    original_price = original_price_elem[0].text.strip() if original_price_elem else current_price

                    try:
                        current_price_val = float(current_price.replace("$", ""))
                        original_price_val = float(original_price.replace("$", ""))
                        discount = int(round((original_price_val - current_price_val) / original_price_val * 100)) if original_price_val > current_price_val else 0
                    except:
                        current_price_val = original_price_val = discount = None

                    deals.append({
                        "title": title,
                        "style": style,
                        "price": current_price,
                        "original_price": original_price,
                        "discount": discount,
                        "url": variant_url,
                    })

                except Exception as e:
                    print(f"⚠️  Failed to scrape variant: {variant_url} due to error: {type(e).__name__}")
                    continue

        except Exception as e:
            print(f"❌ Failed to scrape {link} due to error: {type(e).__name__}")

    driver.quit()
    return deals

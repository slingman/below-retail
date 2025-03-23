#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def get_footlocker_colorways():
    """
    Searches Footlocker.com for "air max 1", selects the first product result,
    then visits its product page. On that page it clicks the "Details" tab (if needed)
    and then iterates over the colorway buttons to extract:
      - Product number (from the first span in the details panel)
      - Supplier SKU (from the second span in the details panel)
      - Sale price and regular price from the price block.
    Returns a list of dictionaries.
    """
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    driver = init_driver()
    deals = []
    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")
        if not product_cards:
            print("No Foot Locker products found.")
            return deals
        # Use the first product.
        first_card = product_cards[0]
        prod_url = first_card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
        print("Foot Locker product URL:", prod_url)
        driver.get(prod_url)
        time.sleep(5)
        # Click the Details tab if available.
        try:
            details_tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
            details_tab.click()
            time.sleep(2)
        except Exception:
            print("Details tab not found or already open.")
        # Print base product number and supplier SKU for reference.
        try:
            base_product = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]").text.strip()
        except Exception:
            base_product = ""
        try:
            base_supplier = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[2]").text.strip()
        except Exception:
            base_supplier = ""
        print("Base Product #:", base_product, "Supplier SKU:", base_supplier)
        # Find all colorway buttons.
        try:
            buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
            print("Found", len(buttons), "colorway buttons.")
        except Exception as e:
            print("Error finding colorway buttons:", e)
            buttons = []
        # For each button, click and extract variant info.
        for btn in buttons:
            try:
                btn.click()
                time.sleep(5)
                prod_number = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]").text.strip()
                supp_sku = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[2]").text.strip()
                try:
                    sale_price = driver.find_element(By.XPATH, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-final')]").text.strip().replace("$", "")
                except Exception:
                    sale_price = ""
                try:
                    regular_price = driver.find_element(By.XPATH, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-original')]").text.strip().replace("$", "")
                except Exception:
                    regular_price = ""
                deals.append({
                    "product_number": prod_number,
                    "supplier_sku": supp_sku,
                    "sale_price": sale_price,
                    "regular_price": regular_price
                })
            except Exception as e:
                print("Error processing a colorway button:", e)
    except Exception as e:
        print("Error in Foot Locker scraper:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    return deals

if __name__ == "__main__":
    results = get_footlocker_colorways()
    for r in results:
        print(r)

#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    # Uncomment the following line to run in headless mode if desired.
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def click_details_tab(driver):
    try:
        # Click the details tab only once per product.
        details_tab = driver.find_element(By.XPATH, "//a[contains(@href, '#ProductDetails-tabs-details-panel')]")
        details_tab.click()
        # Wait until the details panel is visible.
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ProductDetails-tabs-details-panel"))
        )
        print("Clicked details tab successfully.")
    except NoSuchElementException as e:
        print("Details tab not found:", e)
    except TimeoutException as e:
        print("Timeout waiting for details tab content:", e)

def get_details_panel(driver):
    try:
        details_panel = driver.find_element(By.ID, "ProductDetails-tabs-details-panel")
        return details_panel
    except NoSuchElementException:
        print("Details panel not found.")
        return None

def process_colorway(driver, colorway_button, details_panel):
    try:
        # Click the colorway button to update the product details.
        colorway_button.click()
        # Wait briefly to allow the details panel to update.
        time.sleep(1)  # You might consider replacing this with a more robust explicit wait.
        
        # Extract product number from the details panel.
        try:
            product_number = details_panel.find_element(By.XPATH, ".//div[contains(@class, 'product-number')]").text
        except NoSuchElementException:
            product_number = "N/A"
        
        # Extract supplier SKU from the details panel.
        try:
            supplier_sku = details_panel.find_element(By.XPATH, ".//div[contains(@class, 'supplier-sku')]").text
        except NoSuchElementException:
            supplier_sku = None
        
        return product_number, supplier_sku
    except Exception as e:
        print("Error processing colorway:", e)
        return None, None

def process_product(driver, product_url):
    print(f"\nProcessing product URL: {product_url}")
    driver.get(product_url)
    time.sleep(2)  # Allow time for the page to load
    
    # Click the details tab only once.
    click_details_tab(driver)
    
    # Get the details panel which will be reused for each colorway.
    details_panel = get_details_panel(driver)
    if not details_panel:
        print("Skipping product due to missing details panel.")
        return
    
    # Locate colorway buttons. (Adjust the CSS selector to match the actual page structure.)
    try:
        colorway_buttons = driver.find_elements(By.CSS_SELECTOR, ".colorway-selector button")
        if not colorway_buttons:
            print("No colorways found for product.")
            return
    except Exception as e:
        print("Error finding colorway buttons:", e)
        return
    
    for idx, button in enumerate(colorway_buttons, start=1):
        print(f"Processing colorway {idx}...")
        product_number, supplier_sku = process_colorway(driver, button, details_panel)
        if supplier_sku:
            print(f"Extracted -> Product Number: {product_number}, Supplier SKU: {supplier_sku}")
        else:
            print(f"Could not extract Supplier SKU for colorway {idx}.")

def main():
    driver = setup_driver()
    product_urls = [
        "https://www.footlocker.com/product/nike-air-max-1-mens/Z4549101.html",
        "https://www.footlocker.com/product/nike-air-max-1-mens/Z5808102.html",
        # Add additional product URLs as needed.
    ]
    for url in product_urls:
        process_product(driver, url)
    driver.quit()

if __name__ == "__main__":
    main()

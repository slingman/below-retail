# scrapers/sneakers/nike.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver


def scrape_nike_air_max_1():
    print("Finding Nike Air Max 1 deals...\n")

    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()
    driver.get(search_url)
    time.sleep(3)

    product_links = set()
    elements = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
    for el in elements:
        href = el.get_attribute("href")
        if href:
            product_links.add(href)

    print(f"Found {len(product_links)} product links.\n")

    for link in product_links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2"))
            )

            title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text

            # New selector for style ID — double check in browser dev tools if it breaks again
            style_id_el = driver.find_element(By.XPATH, "//div[contains(text(),'Style:')]/following-sibling::div")
            style_id = style_id_el.text.strip()

            try:
                sale_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price-reduced]").text
                full_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]").text
            except:
                full_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]").text
                sale_price = None

            print(f"🟢 {title}")
            print(f"    Style ID: {style_id}")
            print(f"    Price: {sale_price or full_price}")
            if sale_price:
                print(f"    Original Price: {full_price}")
            print(f"    URL: {link}\n")

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")

    driver.quit()

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.selenium_setup import create_webdriver

def scrape_nike_air_max_1():
    base_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver(headless=False)

    try:
        print("Finding product links...")
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay"))
        )
        links = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        product_links = list(set([link.get_attribute("href") for link in links if link.get_attribute("href")]))
        print(f"Found {len(product_links)} product links.\n")

        results = []
        for url in product_links:
            try:
                driver.get(url)
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "description-preview__style-color"))
                )

                title = driver.find_element(By.CLASS_NAME, "headline-2.css-15gyvwk").text
                style_id = driver.find_element(By.CLASS_NAME, "description-preview__style-color").text
                price_els = driver.find_elements(By.CLASS_NAME, "product-price")
                price = None
                sale_price = None

                if len(price_els) == 1:
                    price = price_els[0].text.replace("$", "").strip()
                elif len(price_els) >= 2:
                    price = price_els[0].text.replace("$", "").strip()
                    sale_price = price_els[1].text.replace("$", "").strip()

                results.append({
                    "title": title,
                    "style_id": style_id,
                    "price": price,
                    "sale_price": sale_price
                })

            except Exception as e:
                print(f"Failed to scrape {url} due to error: {e}")

        return results

    finally:
        driver.quit()

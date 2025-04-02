import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver

def scrape_nike_air_max_1():
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air+max+1&vst=air%20max%201"

    driver = create_webdriver()
    driver.get(search_url)
    time.sleep(2)

    print("Finding product links...")
    product_links = set()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay"))
        )
        links = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        for link in links:
            href = link.get_attribute("href")
            if href and "air-max-1" in href.lower():
                product_links.add(href)
    except Exception as e:
        print("Failed to extract product links:", e)
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")
    results = []

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(2)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2"))
            )

            title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text.strip()

            # Try to extract style ID, fallback to regex
            try:
                style_id = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
            except:
                match = re.search(r'/([A-Z0-9]{6}-[0-9]{3})$', link)
                style_id = match.group(1) if match else "N/A"

            try:
                sale_price = driver.find_element(By.CSS_SELECTOR, ".product-price--is-sale").text.strip()
                full_price = driver.find_element(By.CSS_SELECTOR, ".product-price.us__styling").text.strip()
            except:
                full_price = driver.find_element(By.CSS_SELECTOR, ".product-price").text.strip()
                sale_price = None

            results.append({
                "title": title,
                "style_id": style_id,
                "price": sale_price if sale_price else full_price,
                "sale_price": sale_price,
                "url": link
            })

        except Exception as e:
            print(f"Failed to scrape {link} due to error:", e)
            continue

    driver.quit()
    return results

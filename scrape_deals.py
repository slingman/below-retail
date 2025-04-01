from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
import time


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=chrome")  # changed from "--headless=new"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def extract_variant_data(driver):
    variants = []
    try:
        swatches = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='colorway'] button"))
        )

        for idx, swatch in enumerate(swatches):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", swatch)
                time.sleep(0.5)
                swatch.click()
                time.sleep(1.5)

                title = driver.find_element(By.CSS_SELECTOR, "h1.headline-5").text.strip()
                style_id = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-style-colorway']").text.strip()

                try:
                    sale_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-reduced']").text.strip()
                    regular_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-original']").text.strip()
                except:
                    sale_price = None
                    try:
                        regular_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price']").text.strip()
                    except:
                        regular_price = "N/A"

                variants.append({
                    "title": title,
                    "style_id": style_id,
                    "price": regular_price,
                    "sale_price": sale_price,
                })

            except Exception as e:
                print(f"Failed to extract variant at index {idx}: {e}")
                continue

    except TimeoutException:
        print("Variant swatches not found.")
    return variants


def scrape_nike_air_max_1():
    base_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = setup_driver()
    driver.get(base_url)
    time.sleep(4)

    product_links = []
    try:
        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay"))
        )
        product_links = list(set([card.get_attribute("href") for card in cards]))
    except:
        print("Failed to find product cards.")
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")
    all_products = []

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(3)

            title = driver.find_element(By.CSS_SELECTOR, "h1.headline-5").text.strip()
            base_style = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-style-colorway']").text.strip()

            try:
                sale_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-reduced']").text.strip()
                regular_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-original']").text.strip()
            except:
                sale_price = None
                try:
                    regular_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price']").text.strip()
                except:
                    regular_price = "N/A"

            variants = extract_variant_data(driver)

            print(f"Product: {title}")
            print(f"Base Style: {base_style}")
            print(f"Price: {regular_price}")
            if sale_price:
                print(f"Sale Price: {sale_price}")
            print("Variants:")
            for var in variants:
                discount = ""
                if var["sale_price"]:
                    try:
                        p1 = float(var["price"].replace("$", ""))
                        p2 = float(var["sale_price"].replace("$", ""))
                        discount = f" ({round((p1 - p2) / p1 * 100)}% off)"
                    except:
                        discount = ""
                print(f"  - {var['style_id']}: {var['sale_price'] or var['price']}{discount}")
            print()

            all_products.append({
                "title": title,
                "base_style": base_style,
                "price": regular_price,
                "sale_price": sale_price,
                "variants": variants
            })

        except WebDriverException as e:
            print(f"Failed to scrape {link} due to error: {e}")
            continue

    driver.quit()
    return all_products

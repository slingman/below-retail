import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver

BASE_URL = "https://www.nike.com"
SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    print("Finding product links...")
    driver = create_webdriver()
    driver.get(SEARCH_URL)

    time.sleep(2)
    product_links = []

    try:
        product_cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        for card in product_cards:
            href = card.get_attribute("href")
            if href and href.startswith("https://www.nike.com/t/air-max-1"):
                product_links.append(href)
    except Exception as e:
        print(f"Failed to extract product links: {e}")
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")

    results = []
    for url in product_links:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".description-preview__style-color"))
            )

            title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2.css-15ysz1q").text.strip()
            style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
            price_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']")
            price_text = price_elem.text.strip().replace("\n", " ")

            variants = []
            try:
                color_buttons = driver.find_elements(By.CSS_SELECTOR, "li[class*='colorway']")
                for i, btn in enumerate(color_buttons):
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    btn.click()
                    time.sleep(2)
                    variant_style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
                    price_text_variant = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']").text.strip().replace("\n", " ")
                    variants.append({
                        "style_id": variant_style,
                        "price": price_text_variant
                    })
            except:
                pass

            results.append({
                "url": url,
                "title": title,
                "style_id": style,
                "price": price_text,
                "variants": variants
            })

        except Exception as e:
            print(f"Failed to scrape {url} due to error: {e}\n")
            continue

    driver.quit()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for product in results:
        print(f"{product['title']} ({product['style_id']}): {product['price']}")
        for v in product['variants']:
            print(f"  - {v['style_id']}: {v['price']}")
        print()

    print("Summary:")
    print(f"  Total unique products: {len(results)}")
    print(f"  Total colorway variants: {sum(len(p['variants']) for p in results)}")
    return results

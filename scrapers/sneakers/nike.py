import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver

def scrape_nike_air_max_1():
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air%20max%201&vst=air%20max%201"

    driver = create_webdriver(headless=False)
    driver.get(search_url)
    time.sleep(3)

    print("Finding product links...")
    product_links = []
    try:
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay"))
        )
        product_links = [card.get_attribute("href") for card in product_cards]
        print(f"Found {len(product_links)} product links.\n")
    except Exception as e:
        print(f"Failed to extract product links: {e}")
        driver.quit()
        return []

    results = []

    for i, link in enumerate(product_links[:25]):
        print(f"Scraping product {i + 1}: {link}")
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1#pdp_product_title"))
            )
            title = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text.strip()

            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="currentPrice-container"]')
                price = price_elem.text.strip()
            except:
                price = "N/A"

            try:
                style_elem = driver.find_element(By.XPATH, "//li[contains(text(),'Style')]")
                style = style_elem.text.split("Style:")[-1].strip()
            except:
                style = "N/A"

            results.append({
                "title": title,
                "price": price,
                "style": style,
                "url": link
            })

        except Exception as e:
            print(f"❌ Could not scrape {link} due to error: {e}\n")

    driver.quit()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for item in results:
        print(f"{item['title']} ({item['style']}) - {item['price']}")
        print(f"  {item['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(results)}")
    return results

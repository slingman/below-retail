import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver

def scrape_nike_air_max_1():
    print("Finding Nike Air Max 1 deals...\n")
    driver = create_webdriver(headless=True)
    wait = WebDriverWait(driver, 10)

    deals = []
    try:
        # Go to Nike search results page for Air Max 1
        url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
        driver.get(url)
        time.sleep(4)

        print("Finding product links...")
        product_links = []
        cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        product_links = list({card.get_attribute("href") for card in cards if card.get_attribute("href")})
        print(f"Found {len(product_links)} product links.\n")

        for idx, link in enumerate(product_links):
            print(f"Scraping product {idx + 1}: {link}")
            try:
                driver.get(link)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1#pdp_product_title')))

                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1#pdp_product_title').text.strip()
                except:
                    print("❌ Could not find product title.\n")
                    continue

                try:
                    style_id_elem = driver.find_element(By.XPATH, '//li[contains(text(),"Style:")]')
                    style_id = style_id_elem.text.split("Style:")[-1].strip()
                except:
                    style_id = "N/A"

                try:
                    current_price_elem = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="currentPrice-container"]')
                    current_price = current_price_elem.text.strip()
                except:
                    current_price = "N/A"

                try:
                    original_price_elem = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="initialPrice-container"]')
                    original_price = original_price_elem.text.strip()
                except:
                    original_price = current_price  # fallback if not on sale

                deal = {
                    "title": title,
                    "style_id": style_id,
                    "current_price": current_price,
                    "original_price": original_price,
                    "url": link,
                }

                if current_price != original_price and current_price != "N/A" and original_price != "N/A":
                    try:
                        current_float = float(current_price.replace("$", ""))
                        original_float = float(original_price.replace("$", ""))
                        discount_percent = round((original_float - current_float) / original_float * 100)
                        deal["discount_percent"] = discount_percent
                    except:
                        pass

                deals.append(deal)
            except Exception as e:
                print(f"Failed to scrape {link} due to error: {e}\n")

    finally:
        driver.quit()
    return deals

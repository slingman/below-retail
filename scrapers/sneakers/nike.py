from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_nike_deals():
    url = "https://www.nike.com/w?q=air+max+1"

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for efficiency
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    deals = []
    try:
        driver.get(url)
        time.sleep(5)  # Allow search results to load

        product_cards = driver.find_elements(By.CLASS_NAME, "product-card")
        product_urls = []
        for card in product_cards:
            try:
                try:
                    product_url = card.find_element(By.CLASS_NAME, "product-card__link-overlay").get_attribute("href")
                except:
                    product_url = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__link-overlay']").get_attribute("href")
                product_urls.append(product_url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
        
        for prod_url in product_urls:
            try:
                driver.get(prod_url)
                time.sleep(5)  # Allow detail page to load

                try:
                    product_title = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text.strip()
                except Exception as e:
                    try:
                        product_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='product_title']").text.strip()
                    except Exception as e:
                        product_title = "Unknown Product Title"
                        print(f"⚠️ Could not extract product title: {e}")

                style_id = prod_url.split("/")[-1]
                print(f"✅ Nike Style ID Extracted: {style_id}")

                try:
                    sale_price_text = driver.find_element(By.CSS_SELECTOR, "span[data-testid='currentPrice-container']").text
                    sale_price = sale_price_text.replace("$", "").strip()
                except Exception as e:
                    sale_price = None

                try:
                    regular_price_text = driver.find_element(By.CSS_SELECTOR, "span[data-testid='initialPrice-container']").text
                    regular_price = regular_price_text.replace("$", "").strip()
                except Exception as e:
                    regular_price = sale_price

                try:
                    discount_percent = driver.find_element(By.CSS_SELECTOR, "span[data-testid='OfferPercentage']").text.strip()
                except Exception as e:
                    discount_percent = None

                try:
                    sale_price = float(sale_price) if sale_price else None
                    regular_price = float(regular_price) if regular_price else None
                except:
                    sale_price, regular_price = None, None

                print(f"🟢 Nike Product Found: {product_title} | Sale Price: {sale_price} | Regular Price: {regular_price} | Style ID: {style_id}")

                deals.append({
                    "store": "Nike",
                    "product_name": product_title,
                    "product_url": prod_url,
                    "sale_price": sale_price,
                    "regular_price": regular_price,
                    "discount_percent": discount_percent,
                    "style_id": style_id,
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()

if __name__ == "__main__":
    deals = get_nike_deals()
    for deal in deals:
        print(deal)

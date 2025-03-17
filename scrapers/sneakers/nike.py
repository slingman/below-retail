import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_nike_deals():
    """
    Scrapes Nike Air Max 1 deals from Nike's website and returns them in a structured format.

    Returns:
        list: A list of dictionaries containing product name, price, link, and style_id.
    """

    print("\n🔍 Accessing Nike deals...\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://www.nike.com/w?q=air+max+1"
    driver.get(base_url)
    time.sleep(5)  # Allow page to load

    nike_deals = []

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-card")
        for product in products:
            try:
                name_element = product.find_element(By.CSS_SELECTOR, "div.product-card__title")
                price_element = product.find_element(By.CSS_SELECTOR, "div.product-price")
                link_element = product.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay")
                style_id_element = product.find_element(By.CSS_SELECTOR, "div.product-card__style-color")

                name = name_element.text.strip()
                price_final = price_element.text.strip()
                link = link_element.get_attribute("href")
                style_id = style_id_element.text.strip().split(" ")[-1]  # Extract last part (actual style ID)

                nike_deals.append({
                    "name": name,
                    "price_final": price_final,
                    "link": link,
                    "style_id": style_id
                })

                print(f"✅ Found Nike Air Max 1: {name} - {price_final} - {style_id}")

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    except Exception as e:
        print(f"❌ Error scraping Nike: {e}")

    driver.quit()

    print(f"\n🎯 Total Nike Air Max 1 deals found: {len(nike_deals)}\n")
    return nike_deals


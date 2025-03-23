import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_nike_colorways(base_url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    print(f"🔍 Fetching base product page: {base_url}")
    driver.get(base_url)
    time.sleep(2)

    # Accept cookie banner if present
    try:
        consent_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All Cookies')]"))
        )
        consent_button.click()
        print("✅ Cookie consent accepted")
    except:
        print("ℹ️ No cookie consent dialog found")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract base product info
    product_title = soup.find('h1', {'data-testid': 'product_title'})
    product_title = product_title.text.strip() if product_title else 'N/A'

    style_id_tag = soup.find('li', {'data-testid': 'product-description-style-color'})
    base_style_id = style_id_tag.text.strip().replace("Style: ", "") if style_id_tag else 'N/A'

    current_price_tag = soup.find('span', {'data-testid': 'currentPrice-container'})
    sale_price = current_price_tag.text.strip() if current_price_tag else 'N/A'

    original_price_tag = soup.find('span', {'data-testid': 'initialPrice-container'})
    original_price = original_price_tag.text.strip() if original_price_tag else sale_price

    print("\n🎯 Base Product Info")
    print(f"Name: {product_title}")
    print(f"Style ID: {base_style_id}")
    print(f"Price: {original_price}")
    if original_price != sale_price:
        print(f"Sale Price: {sale_price}")

    # Get all colorways from the base page
    colorway_links = soup.select('a[data-testid^="colorway-link"]')
    colorway_urls = [f"https://www.nike.com{a['href']}" for a in colorway_links]
    unique_colorways = list(set(colorway_urls))

    colorway_data = []
    print("\n🎨 Fetching other colorways:")
    for idx, url in enumerate(unique_colorways):
        try:
            driver.get(url)
            time.sleep(1.5)
            swatch = BeautifulSoup(driver.page_source, 'html.parser')

            title = swatch.find('h1', {'data-testid': 'product_title'})
            title = title.text.strip() if title else 'N/A'

            style_id = swatch.find('li', {'data-testid': 'product-description-style-color'})
            style_id = style_id.text.strip().replace("Style: ", "") if style_id else 'N/A'

            current_price = swatch.find('span', {'data-testid': 'currentPrice-container'})
            sale = current_price.text.strip() if current_price else 'N/A'

            original = swatch.find('span', {'data-testid': 'initialPrice-container'})
            retail = original.text.strip() if original else sale

            colorway_data.append({
                'style_id': style_id,
                'price': retail,
                'sale_price': sale if sale != retail else None
            })

            print(f"[{idx+1}] Style ID: {style_id}, Price: {retail}, Sale Price: {sale if sale != retail else 'N/A'}")

        except Exception as e:
            print(f"⚠️ Error fetching colorway at {url}: {e}")
            continue

    driver.quit()

    return {
        'base_product': {
            'title': product_title,
            'style_id': base_style_id,
            'price': original_price,
            'sale_price': sale_price if original_price != sale_price else None,
        },
        'other_colorways': colorway_data
    }


# Example usage:
if __name__ == "__main__":
    base_url = "https://www.nike.com/t/air-max-1-essential-mens-shoes-2C5sX2/FZ5808-400"
    result = get_nike_colorways(base_url)
    print("\n✅ Done fetching Nike product variants.")

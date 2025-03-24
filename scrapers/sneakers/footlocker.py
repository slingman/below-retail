import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.common import extract_price


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_footlocker_deals():
    driver = create_driver()
    base_url = "https://www.footlocker.com/search?query=air%20max%201"

    print("\nFetching Foot Locker deals...")
    driver.get(base_url)
    time.sleep(2)

    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_button.click()
    except:
        print("ℹ️ No cookie consent dialog found")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ProductCard"))
    )
    product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")
    print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

    product_urls = []
    for card in product_cards:
        try:
            link = card.find_element(By.CSS_SELECTOR, "a.ProductCard-link")
            product_urls.append(link.get_attribute("href"))
        except:
            continue

    print(f"Extracted product URLs: {product_urls[:10]}{'...' if len(product_urls) > 10 else ''}\n")

    deals = []
    seen_skus = set()

    for idx, url in enumerate(product_urls[:10]):
        print(f"🔄 Processing Foot Locker product [{idx + 1}]...")
        driver.get(url)
        time.sleep(2)

        try:
            title = driver.find_element(By.CLASS_NAME, "ProductDetails-title").text.strip()
        except:
            title = f"Product {idx + 1}"
            print(f"⚠️ Could not extract product title, using '{title}'")

        print(f"📝 Product Title: {title}")

        try:
            details_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Details')]"))
            )
            details_tab.click()
            print("✅ Clicked on 'Details' tab")
        except:
            print("⚠️ Warning: Could not click 'Details' tab")

        try:
            base_number = driver.current_url.split("/")[-1].replace(".html", "")
        except:
            base_number = "Unknown"

        print(f"Base Product Number: {base_number}")

        variant_buttons = driver.find_elements(By.CSS_SELECTOR, "div.ColorSwatch")
        print(f"🎨 Found {len(variant_buttons)} colorways for product [{idx + 1}].")

        variant_data = []

        for v_idx, button in enumerate(variant_buttons):
            print(f"\n🔄 Processing colorway [{v_idx + 1}] for {title}...")
            try:
                details_tab = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Details')]"))
                )
                details_tab.click()
            except:
                pass

            time.sleep(1)

            # Click variant
            try:
                driver.execute_script("arguments[0].click();", button)
            except:
                print("⚠️ Failed to click colorway")
                continue

            # Wait for product number to update
            new_number = base_number
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: d.current_url.split("/")[-1].replace(".html", "") != base_number
                )
                new_number = driver.current_url.split("/")[-1].replace(".html", "")
            except:
                print("⚠️ Timeout waiting for product number update; assuming base product remains")

            if new_number != base_number:
                variant_url = f"https://www.footlocker.com/product/~/{new_number}.html"
                print(f"Updated Product Number: {new_number}")
                print(f"Navigating to variant URL: {variant_url}")
                driver.get(variant_url)
                time.sleep(1)
                try:
                    details_tab = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Details')]"))
                    )
                    details_tab.click()
                except:
                    pass

            try:
                supplier_sku = driver.find_element(By.XPATH, "//div[contains(text(),'Style')]/following-sibling::div").text.strip()
                print(f"Extracted Supplier SKU: {supplier_sku}")
            except:
                supplier_sku = "N/A"

            # Extract price info
            price = extract_price(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-final')]")
            original = extract_price(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-original')]")
            discount = extract_price(driver, "//div[contains(@class, 'ProductPrice-percent')]")

            if price or original:
                print(f"Price Info: {price} {original or ''} {discount or ''}")
            else:
                print("⚠️ Warning: Could not extract price info.")
                price = original = discount = None

            if supplier_sku not in seen_skus:
                seen_skus.add(supplier_sku)
                variant_data.append({
                    "title": title,
                    "style_id": supplier_sku,
                    "price": price,
                    "retail_price": original,
                    "discount": discount
                })

        deals.extend(variant_data)

    driver.quit()

    print(f"\nSUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}\n")
    print(f"Fetched {len(deals)} Foot Locker deals.\n")

    return deals

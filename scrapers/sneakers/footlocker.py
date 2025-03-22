#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def get_element_text(driver, xpath):
    try:
        elem = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(1)
        text = elem.text.strip()
        if not text:
            text = elem.get_attribute("innerText").strip()
        return text
    except Exception as e:
        print(f"⚠️ Warning: Could not get text from {xpath}. Returning empty string.")
        return ""

def extract_product_number(text):
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def extract_supplier_sku(driver):
    try:
        spans = driver.find_elements(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']//span")
        for span in spans:
            txt = span.text.strip()
            if "Supplier-sku" in txt:
                m = re.search(r"Supplier-sku #:\s*(\S+)", txt)
                if m:
                    return m.group(1)
        return ""
    except Exception as e:
        print(f"⚠️ Error extracting supplier SKU: {e}")
        return ""

def open_details_tab(driver, details_panel_xpath):
    try:
        panel = driver.find_element(By.XPATH, details_panel_xpath)
        if "open" not in panel.get_attribute("class"):
            try:
                tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                driver.execute_script("arguments[0].click();", tab)
                print("✅ Clicked on 'Details' section to open it")
                time.sleep(3)
            except Exception:
                print("⚠️ Could not click the Details tab; proceeding anyway")
        else:
            print("🔄 'Details' section is already open")
    except Exception:
        print("⚠️ Details panel not found; proceeding anyway")

def process_colorway(prod_url, color_index, details_panel_xpath, product_num_xpath):
    """
    Processes a single colorway variant in its own driver session.
    """
    driver = init_driver()
    deal = None
    try:
        driver.get(prod_url)
        time.sleep(8)
        open_details_tab(driver, details_panel_xpath)
        time.sleep(3)
        base_text = get_element_text(driver, product_num_xpath)
        base_prod = extract_product_number(base_text)
        print("Base Product Number:", base_prod)
        # Get all colorway buttons on this product page.
        colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
        if color_index >= len(colorway_buttons):
            print(f"⚠️ No colorway button at index {color_index+1}.")
            return None
        color_button = colorway_buttons[color_index]
        try:
            actions = ActionChains(driver)
            actions.move_to_element(color_button).click().perform()
            print(f"✅ Clicked on colorway [{color_index+1}]")
        except Exception as e:
            print(f"⚠️ ActionChains click failed: {e}")
            driver.execute_script("arguments[0].click();", color_button)
        driver.execute_script("window.dispatchEvent(new Event('resize'));")
        time.sleep(15)
        updated_text = get_element_text(driver, product_num_xpath)
        updated_prod = extract_product_number(updated_text)
        print("Updated Product Number:", updated_prod)
        # If the updated product number differs, navigate to the variant URL.
        if updated_prod and updated_prod != base_prod:
            variant_url = f"https://www.footlocker.com/product/~/{updated_prod}.html"
            print("Navigating to variant URL:", variant_url)
            driver.get(variant_url)
            time.sleep(8)
            open_details_tab(driver, details_panel_xpath)
            time.sleep(3)
        else:
            print("Base product remains; using current page for variant")
        supplier_sku = extract_supplier_sku(driver)
        print("Extracted Supplier SKU:", supplier_sku)
        if not supplier_sku:
            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}].")
            return None
        sale_price = get_element_text(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-final')]")
        regular_price = get_element_text(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-original')]")
        discount_percent = get_element_text(driver, "//div[contains(@class, 'ProductPrice-percent')]")
        print("Price Info:", sale_price, regular_price, discount_percent)
        deal = {
            "store": "Foot Locker",
            "product_url": prod_url,
            "product_number": updated_prod if updated_prod else base_prod,
            "supplier_sku": supplier_sku,
            "sale_price": sale_price,
            "regular_price": regular_price,
            "discount_percent": discount_percent,
            "colorway_index": color_index+1
        }
    except Exception as e:
        print(f"⚠️ Error processing colorway [{color_index+1}]:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    return deal

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    deals = []
    # Use one driver to get product URLs.
    driver = init_driver()
    try:
        driver.get(search_url)
        time.sleep(8)
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(@id,'accept')]"))
            ).click()
            print("✅ Clicked cookie consent")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found")
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return deals
        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")
        product_urls = []
        for card in product_cards[:3]:
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
    except Exception as e:
        print("⚠️ Error processing search page:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    
    for idx, prod_url in enumerate(product_urls, start=1):
        try:
            print(f"\n🔄 Processing product [{idx}]...")
            driver = init_driver()
            driver.get(prod_url)
            time.sleep(8)
            try:
                prod_title = driver.find_element(By.CSS_SELECTOR, "h1.product-title").text.strip()
            except Exception:
                prod_title = f"Product {idx}"
                print(f"⚠️ Could not extract product title, using '{prod_title}'")
            print("📝 Product Title:", prod_title)
            open_details_tab(driver, details_panel_xpath)
            time.sleep(3)
            base_text = get_element_text(driver, product_num_xpath)
            base_prod = extract_product_number(base_text)
            print("Base Product Number:", base_prod)
            try:
                colorway_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                )
                num_colorways = len(colorway_buttons)
                print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
            except Exception:
                print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                num_colorways = 1
            driver.quit()  # Close the driver used for base info.
            
            for color_index in range(num_colorways):
                print(f"\n🔄 Processing colorway [{color_index+1}] for {prod_title}...")
                deal = process_colorway(prod_url, color_index, details_panel_xpath, product_num_xpath)
                if deal:
                    deal["product_title"] = prod_title
                    deals.append(deal)
                else:
                    print(f"⚠️ Skipping colorway [{color_index+1}] for product [{idx}] due to error.")
                time.sleep(3)
        except Exception as e:
            print(f"⚠️ Error processing product [{idx}]:", e)
            traceback.print_exc()
    print("\nSUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}")
    return deals

if __name__ == "__main__":
    print("Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\nFinal Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']}, Sale Price: {deal['sale_price']}, Regular Price: {deal['regular_price']}, Discount: {deal['discount_percent']})")

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
from selenium.common.exceptions import InvalidSessionIdException

def init_driver():
    """Initializes and returns a new Chrome WebDriver with standard options."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def get_element_text(driver, selector, use_css=True):
    """Scroll to the element and return its text (or innerText if .text is empty)."""
    try:
        if use_css:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
        else:
            elem = driver.find_element(By.XPATH, selector)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(1)
        text = elem.text.strip()
        if not text:
            text = elem.get_attribute("innerText").strip()
        return text
    except Exception as e:
        print(f"⚠️ Error getting text from {'CSS' if use_css else 'XPath'} selector [{selector}]: {e}")
        return ""

def extract_product_number(text):
    """Extracts the product number from text like 'Product #: B9660002'."""
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def extract_supplier_sku(driver):
    """
    Searches all span elements in the details panel for text containing "Supplier-sku #:" 
    and returns the extracted SKU.
    """
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
    """Ensures the Details panel is open; if not, clicks the Details tab."""
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

def process_colorway(prod_url, color_index, details_panel_xpath, product_num_xpath,
                     sale_price_css, regular_price_css, discount_percent_css, variant_url_format):
    """
    Processes a single colorway for a given product by initializing its own driver.
    Returns a deal dict (or None if processing fails).
    """
    driver = init_driver()
    deal = None
    try:
        driver.get(prod_url)
        time.sleep(8)
        # (Optional) handle cookie consent here if needed.
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]"))
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except Exception:
            pass

        # Get product title.
        try:
            product_title = driver.find_element(By.CSS_SELECTOR, "h1.product-title").text.strip()
        except Exception:
            try:
                product_title = driver.find_element(By.CLASS_NAME, "ProductName-primary").text.strip()
            except Exception as e:
                product_title = "Unknown Product Title"
                print(f"⚠️ Could not extract product title, using default: {e}")
        print("📝 Product Title:", product_title)

        open_details_tab(driver, details_panel_xpath)
        time.sleep(3)

        base_text = get_element_text(driver, product_num_xpath, use_css=False)
        base_prod = extract_product_number(base_text)
        print("Base Product Number:", base_prod)

        # Refresh the colorway buttons list.
        colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
        if color_index >= len(colorway_buttons):
            print(f"⚠️ No colorway button at index {color_index+1}. Skipping.")
            return None
        color_button = colorway_buttons[color_index]

        try:
            actions = ActionChains(driver)
            actions.move_to_element(color_button).click().perform()
            print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
        except Exception as e:
            print(f"⚠️ ActionChains click failed: {e}")
            driver.execute_script("arguments[0].click();", color_button)
            print(f"✅ Clicked on colorway [{color_index+1}] using JavaScript fallback")

        driver.execute_script("window.dispatchEvent(new Event('resize'));")
        time.sleep(15)

        updated_text = get_element_text(driver, product_num_xpath, use_css=False)
        updated_prod = extract_product_number(updated_text)
        print("Updated Product Number:", updated_prod)

        if updated_prod and updated_prod != base_prod:
            variant_url = variant_url_format.format(updated_prod)
            print("Navigating to variant URL:", variant_url)
            driver.get(variant_url)
            time.sleep(8)
            open_details_tab(driver, details_panel_xpath)
            time.sleep(3)
        else:
            print("Base product remains; using current page for variant")

        supplier_sku = extract_supplier_sku(driver)
        print("Extracted Supplier SKU from details panel:", supplier_sku)
        if not supplier_sku:
            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}].")
            return None

        try:
            sale_price_text = driver.find_element(By.CSS_SELECTOR, sale_price_css).text.strip()
            sale_price = float(sale_price_text.replace("$", "").strip())
        except Exception:
            sale_price = None
        try:
            regular_price_text = driver.find_element(By.CSS_SELECTOR, regular_price_css).text.strip()
            regular_price = float(regular_price_text.replace("$", "").strip())
        except Exception:
            regular_price = None
        try:
            discount_percent = driver.find_element(By.CSS_SELECTOR, discount_percent_css).text.strip()
        except Exception:
            discount_percent = None

        try:
            fl_title = driver.find_element(By.CSS_SELECTOR, "h1.product-title").text.strip()
        except Exception:
            fl_title = product_title

        deal = {
            "store": "Foot Locker",
            "product_title": fl_title,
            "product_url": prod_url,
            "product_number": updated_prod if updated_prod else base_prod,
            "supplier_sku": supplier_sku,
            "sale_price": sale_price,
            "regular_price": regular_price,
            "discount_percent": discount_percent,
            "colorway_index": color_index + 1
        }
        print("✅ Stored SKU:", supplier_sku, "with Product #", updated_prod if updated_prod else base_prod)

    except InvalidSessionIdException as e:
        print(f"⚠️ Invalid session detected while processing colorway [{color_index+1}]: {e}")
    except Exception as e:
        print(f"⚠️ Error processing colorway [{color_index+1}]: {e}")
        traceback.print_exc()
    finally:
        driver.quit()
    return deal

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    variant_url_format = "https://www.footlocker.com/product/~/{0}.html"
    
    # Selectors and XPaths.
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    sale_price_css = "div.ProductPrice span.ProductPrice-final"
    regular_price_css = "div.ProductPrice span.ProductPrice-original"
    discount_percent_css = "div.ProductPrice div.ProductPrice-percent"
    
    deals = []
    
    # First, use one driver to get the list of product URLs.
    driver_search = init_driver()
    product_urls = []
    try:
        driver_search.get(search_url)
        time.sleep(8)
        try:
            WebDriverWait(driver_search, 5).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]"))
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")
        
        product_cards = WebDriverWait(driver_search, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return deals
        
        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")
        # For example, process the first 4 products.
        product_cards = product_cards[:4]
        for card in product_cards:
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
        driver_search.quit()
    
    # For each product, first determine how many colorways exist
    for idx, prod_url in enumerate(product_urls, start=1):
        # Use a temporary driver to count colorways.
        driver_temp = init_driver()
        num_colorways = 1
        try:
            driver_temp.get(prod_url)
            time.sleep(8)
            open_details_tab(driver_temp, details_panel_xpath)
            time.sleep(3)
            try:
                colorway_buttons = driver_temp.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                num_colorways = len(colorway_buttons) if colorway_buttons else 1
            except Exception:
                num_colorways = 1
        except Exception as e:
            print(f"⚠️ Error getting colorways for product [{idx}]: {e}")
        finally:
            driver_temp.quit()
        
        print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
        for color_index in range(num_colorways):
            print(f"\n🔄 Processing colorway [{color_index+1}] for product [{idx}]...")
            deal = process_colorway(prod_url, color_index, details_panel_xpath, product_num_xpath,
                                    sale_price_css, regular_price_css, discount_percent_css, variant_url_format)
            if deal:
                deals.append(deal)
            else:
                print(f"⚠️ Skipping colorway [{color_index+1}] for product [{idx}] due to processing error.")
    
    print("\nSUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}")
    return deals

if __name__ == "__main__":
    print("Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\nFinal Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']}, "
              f"Sale Price: {deal['sale_price']}, Regular Price: {deal['regular_price']}, Discount: {deal['discount_percent']})")

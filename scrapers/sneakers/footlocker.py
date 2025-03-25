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
        print(f"⚠️ Error getting text from {xpath}: {e}")
        return ""

def extract_product_number(text):
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def extract_prices(driver):
    try:
        final_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-final')]"
        original_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-original')]"
        percent_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-percent')]"

        final_price = get_element_text(driver, final_xpath)
        original_price = get_element_text(driver, original_xpath)
        percent_off = get_element_text(driver, percent_xpath)

        if not final_price and not original_price:
            return "Price Info: N/A"
        elif final_price and original_price and percent_off:
            return f"Price Info: ${final_price} → ${original_price} ({percent_off})"
        elif final_price and original_price:
            return f"Price Info: ${final_price} → ${original_price}"
        else:
            return f"Price Info: ${final_price or original_price}"
    except Exception as e:
        print("⚠️ Error extracting price info:", e)
        return "Price Info: N/A"

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    variant_url_format = "https://www.footlocker.com/product/~/{0}.html"

    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    supplier_sku_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    deals = []

    try:
        driver.get(search_url)
        time.sleep(8)

        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")

        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        product_urls = []
        for card in product_cards[:3]:
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except:
                continue
        print("Extracted product URLs:", product_urls)

        for idx, prod_url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]: {prod_url}")
                driver.get(prod_url)
                time.sleep(8)

                try:
                    prod_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text.strip()
                    print(f"📝 Product Title: {prod_title}")
                except:
                    prod_title = f"Product {idx}"
                    print(f"⚠️ Could not extract product title, using '{prod_title}'")

                try:
                    panel = driver.find_element(By.XPATH, details_panel_xpath)
                    if "open" not in panel.get_attribute("class"):
                        tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                        driver.execute_script("arguments[0].click();", tab)
                        print("✅ Clicked on 'Details' section to open it")
                        time.sleep(3)
                except:
                    print("⚠️ Details panel not found; proceeding anyway")

                base_text = get_element_text(driver, product_num_xpath)
                base_prod = extract_product_number(base_text)
                print("Base Product Number:", base_prod)

                try:
                    colorway_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                    )
                    num_colorways = len(colorway_buttons)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except:
                    num_colorways = 1
                    colorway_buttons = [None]
                    print(f"⚠️ No colorways found for product [{idx}].")

                for color_index in range(num_colorways):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {prod_title}...")
                        colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                        if color_index >= len(colorway_buttons):
                            continue
                        color_button = colorway_buttons[color_index]

                        # Extract variant product number
                        variant_prod = None
                        try:
                            c_img = color_button.find_element(By.TAG_NAME, "img")
                            c_src = c_img.get_attribute("src")
                            for pat in [r"/([A-Z0-9]{6,10})\?", r"_([A-Z0-9]{6,10})_", r"-([A-Z0-9]{6,10})-"]:
                                m = re.search(pat, c_src)
                                if m:
                                    variant_prod = m.group(1)
                                    break
                        except:
                            pass
                        if not variant_prod:
                            variant_prod = f"UNKNOWN-{color_index+1}"
                        print("Variant Product Number:", variant_prod)

                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(color_button).click().perform()
                            print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
                        except:
                            driver.execute_script("arguments[0].click();", color_button)

                        driver.execute_script("window.dispatchEvent(new Event('resize'));")
                        time.sleep(15)

                        updated_text = get_element_text(driver, product_num_xpath)
                        updated_prod = extract_product_number(updated_text)
                        print("Updated Product Number:", updated_prod)

                        if updated_prod and updated_prod != base_prod:
                            variant_url = variant_url_format.format(updated_prod)
                            print("Navigating to variant URL:", variant_url)
                            driver.get(variant_url)
                            time.sleep(8)

                            open_details_tab(driver, details_panel_xpath)

                        supplier_sku = get_element_text(driver, supplier_sku_xpath)
                        print("Extracted Supplier SKU from span:", supplier_sku)

                        price_info = extract_prices(driver)
                        print(price_info)

                        deals.append({
                            "store": "Foot Locker",
                            "product_title": prod_title,
                            "product_url": prod_url,
                            "product_number": updated_prod if updated_prod else base_prod,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_index+1,
                            "price_info": price_info
                        })

                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_index+1}]:", e)
                        traceback.print_exc()

            except Exception as e:
                print(f"⚠️ Error processing product [{idx}]:", e)
                traceback.print_exc()

    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}")
    return deals

def open_details_tab(driver, details_panel_xpath):
    try:
        panel = driver.find_element(By.XPATH, details_panel_xpath)
        if "open" not in panel.get_attribute("class"):
            tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
            driver.execute_script("arguments[0].click();", tab)
            print("✅ Clicked on 'Details' section on variant page to open it")
            time.sleep(3)
    except:
        print("⚠️ Details panel not found on variant page; proceeding anyway")

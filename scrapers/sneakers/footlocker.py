import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.common import extract_price


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def get_footlocker_deals():
    print("\nFetching Foot Locker deals...")
    driver = create_driver()

    try:
        base_url = "https://www.footlocker.com"
        search_url = f"{base_url}/search?query=air%20max%201"
        driver.get(search_url)
        time.sleep(3)

        print("ℹ️ No cookie consent dialog found")

        product_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'ProductCard')]//a[contains(@href, '/product')]")
        product_urls = list({a.get_attribute("href") for a in product_cards})
        print(f"🔎 Found {len(product_urls)} products on Foot Locker.")
        print("Extracted product URLs:", product_urls[:10], "...")

        all_deals = []

        for idx, url in enumerate(product_urls[:10]):
            print(f"\n🔄 Processing Foot Locker product [{idx + 1}]...")
            try:
                driver.get(url)
                time.sleep(2)

                try:
                    title = driver.find_element(By.XPATH, "//h1").text.strip()
                except:
                    title = f"Product {idx + 1}"
                    print(f"⚠️ Could not extract product title, using '{title}'")

                print(f"📝 Product Title: {title}")

                try:
                    details_tab = driver.find_element(By.XPATH, "//button[contains(text(),'Details')]")
                    details_tab.click()
                    print("✅ Clicked on 'Details' tab")
                except:
                    print("⚠️ Warning: Could not click 'Details' tab")
                    continue

                try:
                    base_product_num = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]").text.strip()
                except:
                    base_product_num = "N/A"

                print(f"Base Product Number: {base_product_num}")

                color_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'SwatchButton')]")
                print(f"🎨 Found {len(color_buttons)} colorways for product [{idx + 1}].")

                for i, btn in enumerate(color_buttons):
                    print(f"\n🔄 Processing colorway [{i + 1}] for Product {idx + 1}...")
                    try:
                        driver.get(url)
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'SwatchButton')]")))
                        color_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'SwatchButton')]")
                        color_buttons[i].click()
                        time.sleep(2)

                        try:
                            updated_product_num = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]").text.strip()
                        except:
                            updated_product_num = base_product_num

                        if updated_product_num != base_product_num:
                            variant_url = f"https://www.footlocker.com/product/~/{updated_product_num}.html"
                            print(f"Navigating to variant URL: {variant_url}")
                            driver.get(variant_url)
                            time.sleep(2)
                        else:
                            print("Base product remains; using current page")

                        try:
                            supplier_sku = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[2]").text.strip()
                        except Exception as e:
                            supplier_sku = ""
                            print(f"⚠️ Error extracting supplier SKU: {e}")

                        final_price_text = get_text_safe(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-final')]")
                        original_price_text = get_text_safe(driver, "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'ProductPrice-original')]")
                        discount_text = get_text_safe(driver, "//div[contains(@class, 'ProductPrice-percent')]")

                        if not any([final_price_text, original_price_text, discount_text]):
                            print("⚠️ Warning: Could not extract price info.")
                            continue

                        price = extract_price(final_price_text)
                        original_price = extract_price(original_price_text)
                        discount = discount_text if discount_text else "None"

                        print(f"Extracted Supplier SKU: {supplier_sku}")
                        print(f"Price Info: ${price} ${original_price} {discount}")

                        deal = {
                            "product_number": updated_product_num,
                            "supplier_sku": supplier_sku,
                            "price": price,
                            "original_price": original_price,
                            "discount": discount,
                            "url": driver.current_url,
                        }
                        all_deals.append(deal)

                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{i + 1}]: {e}")
                        print(f"⚠️ Skipping colorway [{i + 1}] for product [{idx + 1}].")
                        continue

            except Exception as e:
                print(f"⚠️ Error processing product [{idx + 1}]: {e}")
                continue

        print(f"\nSUMMARY RESULTS:\nTotal Foot Locker deals found: {len(all_deals)}\n")
        return all_deals

    finally:
        driver.quit()


def get_text_safe(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        print(f"⚠️ Warning: Could not get text from {xpath}.")
        return ""

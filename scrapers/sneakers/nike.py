import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def get_text_safe(driver, by, value):
    try:
        elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, value)))
        return elem.text.strip()
    except Exception:
        return ""

def get_nike_deals():
    driver = init_driver()
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air%20max%201&vst=air%20max%201"

    deals = []

    try:
        driver.get(search_url)
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(@id,'accept')]"))
            ).click()
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found")

        product_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/t/')]")
        product_urls = list({link.get_attribute("href") for link in product_links if "/t/" in link.get_attribute("href")})
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls)

        for idx, url in enumerate(product_urls[:10], start=1):
            print(f"\n🔄 Processing Nike product [{idx}]...")
            try:
                driver.get(url)
                title = get_text_safe(driver, By.TAG_NAME, "h1")
                print("📝 Product Title:", title)

                try:
                    style_elem = driver.find_element(By.XPATH, "//div[contains(text(),'Style:')]")
                    style = style_elem.text.replace("Style:", "").strip()
                except:
                    style = "N/A"

                try:
                    sale_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price] .is--current-price").text.strip()
                except:
                    sale_price = ""

                try:
                    full_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price] .is--strikethrough").text.strip()
                except:
                    full_price = ""

                print("Base Style:", style)
                print("Base Price Info:", sale_price, full_price)

                deals.append({
                    "product_title": title,
                    "style_id": style,
                    "sale_price": sale_price,
                    "regular_price": full_price,
                    "url": url
                })

                # Look for colorway variants
                variant_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/t/') and contains(@aria-label, 'Color')]")
                variant_urls = list({link.get_attribute("href") for link in variant_links})

                for v_idx, v_url in enumerate(variant_urls, start=1):
                    try:
                        print(f"\n🔄 Processing colorway variant [{v_idx}] - URL: {v_url}")
                        driver.get(v_url)
                        time.sleep(1)
                        style = get_text_safe(driver, By.XPATH, "//div[contains(text(),'Style:')]").replace("Style:", "").strip()
                        sale_price = get_text_safe(driver, By.CSS_SELECTOR, "div[data-test=product-price] .is--current-price")
                        full_price = get_text_safe(driver, By.CSS_SELECTOR, "div[data-test=product-price] .is--strikethrough")

                        print("Variant Style:", style)
                        print("Variant Price Info:", sale_price, full_price)

                        deals.append({
                            "product_title": title,
                            "style_id": style,
                            "sale_price": sale_price,
                            "regular_price": full_price,
                            "url": v_url
                        })
                    except Exception as e:
                        print(f"⚠️ Error processing variant colorway: {e}")
                        traceback.print_exc()

            except Exception as e:
                print(f"⚠️ Error processing Nike product [{idx}]: {e}")
                traceback.print_exc()
    finally:
        driver.quit()

    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(deals)}")
    return deals

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scrape_nike_air_max_1():
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air%20max%201&vst=air%20max%201"

    driver = setup_driver()
    driver.get(search_url)
    time.sleep(5)

    product_links = list(set([
        a.get_attribute("href")
        for a in driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
    ]))

    print(f"Found {len(product_links)} product links.\n")

    results = []
    for link in product_links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2"))
            )

            product_title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text
            price_elements = driver.find_elements(By.CSS_SELECTOR, "div.product-price.is--current-price")
            price_text = price_elements[0].text if price_elements else "N/A"

            try:
                style_id = driver.find_element(By.XPATH, "//div[contains(text(), 'Style:')]").text.split("Style:")[-1].strip()
            except:
                style_id = "N/A"

            regular_price = None
            sale_price = None

            if "Sale" in price_text or "\n" in price_text:
                parts = price_text.split("\n")
                if len(parts) == 2:
                    regular_price = parts[0].replace("$", "").strip()
                    sale_price = parts[1].replace("$", "").strip()
            else:
                regular_price = price_text.replace("$", "").strip()

            variants = []
            color_buttons = driver.find_elements(By.CSS_SELECTOR, "li[data-qa='colorway'] button")
            for i in range(len(color_buttons)):
                driver.get(link)
                time.sleep(2)
                color_buttons = driver.find_elements(By.CSS_SELECTOR, "li[data-qa='colorway'] button")
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(color_buttons[i])).click()
                    time.sleep(2)

                    variant_price_text = driver.find_element(By.CSS_SELECTOR, "div.product-price.is--current-price").text
                    variant_style_id = driver.find_element(By.XPATH, "//div[contains(text(), 'Style:')]").text.split("Style:")[-1].strip()

                    if "\n" in variant_price_text:
                        reg, sale = variant_price_text.split("\n")
                        variant_regular_price = reg.replace("$", "").strip()
                        variant_sale_price = sale.replace("$", "").strip()
                    else:
                        variant_regular_price = variant_price_text.replace("$", "").strip()
                        variant_sale_price = None

                    variants.append({
                        "style_id": variant_style_id,
                        "regular_price": variant_regular_price,
                        "sale_price": variant_sale_price,
                    })

                except Exception as e:
                    print(f"Failed to extract variant {i} on {link}: {e}")

            results.append({
                "title": product_title,
                "url": link,
                "style_id": style_id,
                "regular_price": regular_price,
                "sale_price": sale_price,
                "variants": variants
            })

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")

    driver.quit()
    return results

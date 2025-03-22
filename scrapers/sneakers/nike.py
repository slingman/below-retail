from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import traceback

def get_nike_deals():
    # Set the search URL for "air max 1"
    search_url = "https://www.nike.com/w?q=air+max+1"
    
    # XPaths/CSS selectors for Nike details:
    # These selectors are assumed and may need adjustment.
    details_tab_xpath = "//button[contains(@id, 'pdp-tab-details')]"  # Button to open Details (if present)
    details_panel_xpath = "//div[contains(@class, 'product-details-panel')]"  # Details panel container
    style_number_xpath = "//div[contains(@class, 'product-details-panel')]/span[1]"  # Base style number (assumed)
    # Price selectors (from the existing Nike code)
    sale_price_css = "span[data-testid='currentPrice-container']"
    regular_price_css = "span[data-testid='initialPrice-container']"
    discount_percent_css = "span[data-testid='OfferPercentage']"
    # Assumed class name for colorway buttons on Nike product pages.
    colorway_buttons_class = "ColorwaySelector"
    
    # Set up the driver.
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
    
    deals = []
    
    try:
        driver.get(search_url)
        time.sleep(8)
        
        # Handle cookie consent if present.
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]")
                )
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")
        
        # Get product cards from search results.
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
        )
        if not product_cards:
            print("⚠️ No products found on Nike.")
            return deals
        
        print(f"🔎 Found {len(product_cards)} products on Nike.")
        # Process the first 3 products.
        product_urls = []
        for card in product_cards[:3]:
            try:
                # Use the overlay link to get the product URL.
                product_url = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__link-overlay']").get_attribute("href")
                product_urls.append(product_url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
        
        # Process each product URL.
        for idx, prod_url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]...")
                driver.get(prod_url)
                time.sleep(8)
                
                # Get product title.
                try:
                    prod_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1#pdp_product_title"))
                    ).text.strip()
                    print(f"📝 Product Title: {prod_title}")
                except Exception:
                    try:
                        prod_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='product_title']").text.strip()
                    except Exception as e:
                        prod_title = f"Product {idx}"
                        print(f"⚠️ Could not extract product title, using '{prod_title}'")
                
                # Optionally, click on the Details tab if available.
                try:
                    details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                    driver.execute_script("arguments[0].click();", details_tab)
                    print("✅ Clicked on Details tab")
                    time.sleep(3)
                except Exception:
                    print("ℹ️ Details tab may already be open or not present")
                
                # Extract the base style number from the details panel.
                try:
                    base_text = driver.find_element(By.XPATH, style_number_xpath).text.strip()
                except Exception as e:
                    base_text = ""
                    print(f"⚠️ Could not extract base style number: {e}")
                base_style = base_text  # For Nike, we treat this as the base style.
                print("Base Style:", base_style)
                
                # Get colorway buttons.
                try:
                    colorway_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, colorway_buttons_class))
                    )
                    num_colorways = len(colorway_buttons)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except Exception:
                    print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                    num_colorways = 1
                    colorway_buttons = [None]
                
                # Process

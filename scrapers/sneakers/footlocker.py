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
    """Extracts product number from a string like 'Product #: B9660002'"""
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def open_details_tab(driver, details_panel_xpath):
    """Ensures the details panel is open; if not, clicks the Details tab."""
    try:
        panel = driver.find_element(By.XPATH, details_panel_xpath)
        if "open" not in panel.get_attribute("class"):
            try:
                tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                driver.execute_script("arguments[0].click();", tab)
                print("✅ Clicked on 'Details' section to open it on variant page")
                time.sleep(3)
            except Exception:
                print("⚠️ Could not click details tab on variant page; proceeding anyway")
        else:
            print("🔄 'Details' section is already open on variant page")
    except Exception:
        print("⚠️ Details panel not found on variant page; proceeding anyway")

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    # Use a positional placeholder for the variant URL.
    variant_url_format = "https://www.footlocker.com/product/~/{0}.html"

    # XPaths for details panel elements.
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    supplier_sku_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"

    # Set up WebDriver.
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # For headless mode.
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Ch

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_footlocker_deal(target_style_id):
    url = "https://www.footlocker.com/product/nike-air-max-1-mens/Z5808400.html"  # Single product page

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for page to load

        # Extract Product Name
        product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()

        # Extract Style ID (from product page content)
        style_id_text = None
        try:
            details_section = driver.find_element(By.CLASS_NAME, "ProductDetails")
            details_text = details_section.text
            for line in details_text.split("\n"):
                if "Supplier-sku #" in line:
                    style_id_text = line.split("#")[-1].strip()
                    break
        except:
            style_id_text = None

        # Extract Price
        try:
            price_text = driver.find_element(By.CLASS_NAME, "ProductPrice").text
            price = float(price_text.replace("$", "").split()[0])  # Convert to float
        except:
            price = None  # If price is missing

        # Validate Style ID
        final_style_id = style_id_text if style_id_text else None

        # Check if this matches the target style ID
        if final_style_id == target_style_id:
            return {
                "store": "Foot Locker",
                "product_name": product_name,
                "product_url": url,
                "price": price,
                "style_id": final_style_id
            }
        else:
            return None  # No matching product

    finally:
        driver.quit()

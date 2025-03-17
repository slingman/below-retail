from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_footlocker_deals():
    url = "https://www.footlocker.com/product/nike-air-max-1-mens/Z5808400.html"  # Direct product page

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for page to load

        # Extract Product Name
        try:
            product_name = driver.find_element(By.CLASS_NAME, "ProductName-primary").text
        except:
            product_name = "Unknown Product"

        # Extract Product URL
        product_url = url  # Since we're on the product page

        # Extract Style ID (Supplier-sku #)
        style_id_text = None
        try:
            details_section = driver.find_element(By.CLASS_NAME, "ProductDetails")
            details_text = details_section.text
            print("\nDEBUG: Full product details text from Foot Locker:\n", details_text)  # Debug print

            for line in details_text.split("\n"):
                if "Supplier-sku #" in line:
                    style_id_text = line.split("#")[-1].strip()
                    print(f"✅ Extracted Style ID from Foot Locker: {style_id_text}")  # Debug print
                    break
        except:
            print("⚠️ Unable to extract style ID from Foot Locker")
            style_id_text = None

        # Extract Price
        try:
            price_text = driver.find_element(By.CLASS_NAME, "ProductPrice").text
            print(f"DEBUG: Raw price text from Foot Locker: {price_text}")  # Debug print
            price = float(price_text.replace("$", "").split()[0])  # Convert to float
        except:
            print("⚠️ Unable to extract price from Foot Locker")
            price = None  # If price is missing

        # Store deal information
        deal = {
            "store": "Foot Locker",
            "product_name": product_name,
            "product_url": product_url,
            "price": price,
            "style_id": style_id_text,
        }

        print(f"🟢 Foot Locker Product Found: {product_name} | Price: {price} | Style ID: {style_id_text}")

        return deal

    finally:
        driver.quit()

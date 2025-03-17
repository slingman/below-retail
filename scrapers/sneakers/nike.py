from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_nike_deal(target_style_id):
    url = "https://www.nike.com/t/air-max-1-essential-mens-shoes-2C5sX2/FZ5808-400"  # Single product page

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

        # Extract Style ID from URL
        style_id_url = url.split("/")[-1]  # Last part of the URL contains the style ID

        # Extract Price
        try:
            price_text = driver.find_element(By.CLASS_NAME, "product-price").text
            price = float(price_text.replace("$", "").split()[0])  # Convert to float
        except:
            price = None  # If price is missing

        # Extract Style ID from product page content
        try:
            product_details = driver.find_element(By.CLASS_NAME, "product-description").text
            style_id_text = None
            for line in product_details.split("\n"):
                if "Style:" in line:
                    style_id_text = line.split(":")[-1].strip()
                    break
        except:
            style_id_text = None

        # Validate Style ID
        final_style_id = style_id_text if style_id_text == style_id_url else style_id_url

        # Check if this matches the target style ID
        if final_style_id == target_style_id:
            return {
                "store": "Nike",
                "product_name": product_name,
                "product_url": url,
                "price": price,
                "style_id": final_style_id
            }
        else:
            return None  # No matching product

    finally:
        driver.quit()

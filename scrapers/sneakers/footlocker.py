from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for efficiency
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Foot Locker product page URL (correct format)
url = "https://www.footlocker.com/product/~/Z5808400.html"  # Update this dynamically as needed
driver.get(url)
time.sleep(3)  # Allow time for the page to load

# Locate all available color variants
color_buttons = driver.find_elements(By.CSS_SELECTOR, ".ColorwayStyles-field")

# Iterate through each color option
for index, button in enumerate(color_buttons):
    try:
        ActionChains(driver).move_to_element(button).click().perform()
        time.sleep(3)  # Allow the page to update
        
        # Extract updated SKU and model number from the dynamically updated 'app' div
        app_div = driver.find_element(By.ID, "app")
        sku = app_div.get_attribute("atvec-sku")
        model_number = app_div.get_attribute("atvec-modelnumber")
        list_price = app_div.get_attribute("atvec-listprice")
        original_price = app_div.get_attribute("atvec-originalprice")
        color_name = button.get_attribute("aria-label").replace("Color ", "").strip()
        
        print(f"Color: {color_name}, SKU: {sku}, Model Number: {model_number}, List Price: {list_price}, Original Price: {original_price}")
    except Exception as e:
        print(f"Error processing color {index + 1}: {e}")

# Close the driver
driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for efficiency
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Foot Locker product page URL
url = "https://www.footlocker.com/product/~/Z5808400.html"
driver.get(url)
time.sleep(3)  # Allow time for the page to load

# Locate all color variants
color_buttons = driver.find_elements(By.CSS_SELECTOR, ".ColorwayStyles-field")

# Iterate through each color option
deals = []
for index, button in enumerate(color_buttons):
    try:
        color_name = button.get_attribute("aria-label").replace("Color ", "").strip()

        # Click the color button
        ActionChains(driver).move_to_element(button).click().perform()
        time.sleep(3)  # Allow the page to update

        # Extract SKU & model number from selected button attributes (fallback method)
        sku = button.get_attribute("data-sku")  # Extract SKU directly from button
        model_number = button.get_attribute("data-modelnumber")  # Extract Model Number
        list_price = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price']").text

        # Store deal
        deals.append({
            "Color": color_name,
            "SKU": sku if sku else "N/A",
            "Model Number": model_number if model_number else "N/A",
            "Price": list_price
        })

        print(f"Color: {color_name}, SKU: {sku}, Model Number: {model_number}, Price: {list_price}")

    except Exception as e:
        print(f"Error processing color {index + 1}: {e}")

# Close the driver
driver.quit()

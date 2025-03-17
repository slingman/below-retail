from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Selenium
driver = webdriver.Chrome()
driver.get("https://www.footlocker.com/search?query=Nike%20Air%20Max%201")

# Wait for products to load
wait = WebDriverWait(driver, 10)
products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ProductCard")))

deals = []

for product in products:
    try:
        name = product.find_element(By.CSS_SELECTOR, ".ProductName-primary").text.strip()
        price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice-final").text.strip()

        # Check if there’s an original price (i.e., item is on sale)
        try:
            price_original = product.find_element(By.CSS_SELECTOR, ".ProductPrice-original").text.strip()
        except:
            price_original = price_final  # No sale, just use final price

        link = product.find_element(By.CSS_SELECTOR, ".ProductCard-link").get_attribute("href")

        deals.append({
            "name": name,
            "price_final": price_final,
            "price_original": price_original,
            "link": "https://www.footlocker.com" + link,  # Ensure full URL
        })

    except Exception as e:
        print(f"Error processing product: {e}")

# Print extracted deals
for deal in deals:
    print(deal)

driver.quit()

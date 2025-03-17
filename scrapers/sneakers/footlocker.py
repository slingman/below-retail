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

        # Try sale price first, then original price
        try:
            price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice-final").text.strip()
        except:
            try:
                price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice-original").text.strip()
            except:
                price_final = "Price not found"  # Handle missing price gracefully

        # Extract product link
        link_element = product.find_element(By.CSS_SELECTOR, ".ProductCard-link")
        link = link_element.get_attribute("href")

        # Ensure the base URL is only added when necessary
        if not link.startswith("https://www.footlocker.com"):
            link = "https://www.footlocker.com" + link

        deals.append({
            "name": name,
            "price_final": price_final,
            "link": link,
        })

    except Exception as e:
        print(f"Error processing product: {e}")

# Print extracted deals
for deal in deals:
    print(deal)

driver.quit()

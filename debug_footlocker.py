from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
options=options)

# Load Foot Locker sales page
url = "https://www.footlocker.com/sale/mens/shoes"
driver.get(url)
time.sleep(10)  # Let JavaScript load

# Scroll down multiple times to force content loading
for _ in range(5):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)

# Save the HTML output to a file
html_source = driver.page_source
with open("footlocker_debug.html", "w", encoding="utf-8") as f:
    f.write(html_source)

# Print confirmation message
print("HTML saved to footlocker_debug.html - Open it in Chrome to 
inspect the structure.")

driver.quit()

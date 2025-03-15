import time
import requests
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ✅ Sneaker Sale Sources
SITES = [
    "https://www.nike.com/w/sale-shoes",
    "https://www.adidas.com/us/sale",
    "https://www.footlocker.com/sale/",
    "https://www.finishline.com/store/shop/sale/",
]

# ✅ Rotating User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
]

# ✅ Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Uses new headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

deals = []

for site in SITES:
    print(f"🔍 Scraping {site} - Checking structure...")

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.google.com/search?q={random.randint(100000,999999)}",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    print(f"⚠️ {site} is known for blocking bots, using Selenium first...")
    driver.get(site)
    time.sleep(random.uniform(10, 15))

    # Fake keyboard presses
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(random.uniform(1, 3))

    # Scroll slowly like a human
    scroll_pause_time = random.uniform(2, 4)
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.5);")
        time.sleep(scroll_pause_time)

    # Get page data
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

# ✅ Close Selenium WebDriver
driver.quit()

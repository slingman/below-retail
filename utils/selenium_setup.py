from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

def get_driver():
    """Sets up and returns a Selenium WebDriver instance with headless mode enabled."""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Auto-detect ChromeDriver
    driver_path = "/usr/local/bin/chromedriver"  # Update if necessary

    if not os.path.exists(driver_path):
        raise FileNotFoundError("ChromeDriver not found. Install it or update the path in selenium_setup.py")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

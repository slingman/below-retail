from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_selenium_driver(headless=True):
    """
    Sets up and returns a Selenium WebDriver with Chrome.
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

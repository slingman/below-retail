from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_selenium_driver():
    """Initialize and return a Selenium WebDriver instance for Chrome."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (optional)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver using WebDriver Manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver

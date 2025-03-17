from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_driver():
    """Returns a Selenium WebDriver instance with webdriver-manager handling chromedriver installation."""
    options = Options()
    options.add_argument("--headless")  # Remove this if you want to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Helps avoid detection
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())  # Automates Chromedriver setup
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

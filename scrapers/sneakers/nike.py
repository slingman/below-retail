import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)
from utils.selenium_setup import get_chrome_driver


def scrape_nike_air_max_1():
    url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

    driver = get_chrome_driver()
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    try:
        product_cards = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.product-card__body")
        ))
    except TimeoutException:
        print("Timed out waiting for product cards.")
        driver.quit()
        return []

    product_links = []
    for card in product_cards:
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a.product-card__link-overlay')
            href = link_element.get_attribute("href")
            if href and href not in product_links:
                product_links.append(href)
        except Exception:
            continue

    print(f"Found {len(product_links)} product links.\n")
    results = []

    for link in product_links:
        driver.get(link)
        time.sleep(2)
        wait = WebDriverWait(driver, 10)

        try:
            title = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1.headline-2.css-1qkf1we")
            )).text.strip()
        except TimeoutException:
            title = "N/A"

        try:
            style_id = driver.current_url.strip().split("/")[-1]
        except Exception:
            style_id = "N/A"

        try:
            price_container = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.product-price__wrapper")
            ))
            sale_price_el = price_container.find_element(By.CSS_SELECTOR, "[data-testid='product-price-reduced']")
            reg_price_el = price_container.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
            price = reg_price_el.text.strip()
            sale_price = sale_price_el.text.strip()
        except Exception:
            try:
                price_el = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='product-price']")
                ))
                price = price_el.text.strip()
                sale_price = None
            except Exception:
                price = "N/A"
                sale_price = None

        # Attempt to find all colorway buttons
        try:
            color_buttons = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "button[data-testid='product-cta-colorway']")
            ))
        except TimeoutException:
            color_buttons = []

        variant_data = []
        for btn in color_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                btn.click()
                time.sleep(2)

                variant_style_id = driver.current_url.strip().split("/")[-1]

                try:
                    price_container = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.product-price__wrapper")
                    ))
                    sale_price_el = price_container.find_element(By.CSS_SELECTOR, "[data-testid='product-price-reduced']")
                    reg_price_el = price_container.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
                    variant_price = reg_price_el.text.strip()
                    variant_sale = sale_price_el.text.strip()
                except Exception:
                    try:
                        price_el = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
                        variant_price = price_el.text.strip()
                        variant_sale = None
                    except Exception:
                        variant_price = "N/A"
                        variant_sale = None

                variant_data.append({
                    "style_id": variant_style_id,
                    "price": variant_price,
                    "sale_price": variant_sale
                })

            except StaleElementReferenceException:
                continue
            except WebDriverException:
                continue

        results.append({
            "title": title,
            "style_id": style_id,
            "price": price,
            "sale_price": sale_price,
            "variants": variant_data
        })

        print(f"{title} ({style_id})")
        if sale_price:
            print(f"  Price: {sale_price} (Reg: {price})")
        else:
            print(f"  Price: {price}")
        print(f"  Variants: {len(variant_data)}\n")

    driver.quit()
    return results

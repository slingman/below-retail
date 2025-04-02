import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver


def scrape_nike_air_max_1():
    base_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()

    results = []
    try:
        print("Finding product links...")
        driver.get(base_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay"))
        )
        product_links = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        links = list({link.get_attribute("href") for link in product_links})

        print(f"Found {len(links)} product links.\n")

        for link in links:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2.css-15v1nk6"))
                )
                title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2.css-15v1nk6").text.strip()

                try:
                    style_info = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
                except:
                    style_info = "N/A"

                try:
                    sale_price_elem = driver.find_element(By.CSS_SELECTOR, ".product-price.is--current-price.css-s56yt7")
                    sale_price = sale_price_elem.text.strip()
                except:
                    sale_price = "N/A"

                try:
                    regular_price_elem = driver.find_element(By.CSS_SELECTOR, ".product-price.is--striked.css-0")
                    regular_price = regular_price_elem.text.strip()
                except:
                    regular_price = sale_price  # fallback if not on sale

                print(f"Product: {title}")
                print(f"Style: {style_info}")
                print(f"Price: {regular_price}")
                if sale_price != "N/A" and sale_price != regular_price:
                    print(f"Sale Price: {sale_price}")
                print(f"Link: {link}")
                print("-" * 50)

                results.append({
                    "title": title,
                    "style": style_info,
                    "price": regular_price,
                    "sale_price": sale_price if sale_price != regular_price else None,
                    "link": link,
                })

            except Exception as e:
                print(f"Failed to scrape {link} due to error: {e}")

    except Exception as e:
        print(f"Failed to extract product links: {e}")
    finally:
        driver.quit()

    # Summary
    print("\nFinal Nike Air Max 1 Deals:\n")
    on_sale = [r for r in results if r["sale_price"]]
    print("Summary:")
    print(f"  Total unique products: {len(results)}")
    print(f"  Variants on sale: {len(on_sale)}")

    return results

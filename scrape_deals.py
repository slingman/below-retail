import json
import time
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.adidas import scrape_adidas
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.hibbett import scrape_hibbett
from scrapers.sneakers.nordstrom import scrape_nordstrom
from scrapers.sneakers.dicks import scrape_dicks
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx

# ✅ Define sneaker models to search for
SNEAKER_MODELS = [
    "Nike Air Max 1",
    "Nike Air Max 90",
    "Air Jordan 1",
    "Adidas Ultraboost",
    "New Balance 550",
    "Yeezy Boost 350"
]

# ✅ Store all deals
all_deals = {}

# ✅ Run scrapers for each sneaker model
for model in SNEAKER_MODELS:
    print(f"🔍 Searching for {model} across multiple stores...")

    for scraper in [
        scrape_nike, scrape_adidas, scrape_footlocker,
        scrape_hibbett, scrape_nordstrom, scrape_dicks,
        scrape_goat, scrape_stockx
    ]:
        try:
            print(f"🔍 Checking {scraper.__name__.replace('scrape_', '').capitalize()} for {model}...")
            store_deals = scraper(model)  # Pass the model to each scraper
            
            for product, details in store_deals.items():
                if product not in all_deals:
                    all_deals[product] = details
                else:
                    all_deals[product]["prices"].extend(details["prices"])

            time.sleep(2)  # Prevent rate limits
        except Exception as e:
            print(f"❌ Error in {scraper.__name__}: {e}")

# ✅ Save the scraped deals to `deals.json`
if all_deals:
    with open("deals.json", "w") as f:
        json.dump(all_deals, f, indent=4)
    print(f"✅ Scraped {len(all_deals)} sneaker deals across multiple stores!")
else:
    print("❌ No deals found! Check the scrapers.")

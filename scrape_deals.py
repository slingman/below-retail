import json
import time
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.adidas import scrape_adidas
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx
from scrapers.sneakers.hibbett import scrape_hibbett
from scrapers.sneakers.nordstrom import scrape_nordstrom
from scrapers.sneakers.dicks import scrape_dicks
from scrapers.tech.bestbuy import scrape_bestbuy
from scrapers.tech.amazon import scrape_amazon
from scrapers.tech.walmart import scrape_walmart

# ✅ Define all store scrapers in a list
sneaker_scrapers = [
    scrape_nike,
    scrape_adidas,
    scrape_footlocker,
    scrape_goat,
    scrape_stockx,
    scrape_hibbett,
    scrape_nordstrom,
    scrape_dicks
]

tech_scrapers = [
    scrape_bestbuy,
    scrape_amazon,
    scrape_walmart
]

all_scrapers = sneaker_scrapers + tech_scrapers  # Combine sneaker and tech scrapers

# ✅ Store all deals
all_deals = {}

# ✅ Run each scraper and merge results
for scraper in all_scrapers:
    try:
        print(f"🔍 Scraping {scraper.__name__.replace('scrape_', '').capitalize()}...")
        store_deals = scraper()
        
        for product, details in store_deals.items():
            if product not in all_deals:
                all_deals[product] = details
            else:
                all_deals[product]["prices"].extend(details["prices"])
        
        time.sleep(2)  # Prevent hitting request limits
    except Exception as e:
        print(f"❌ Error in {scraper.__name__}: {e}")

# ✅ Save the scraped deals to `deals.json`
if all_deals:
    with open("deals.json", "w") as f:
        json.dump(all_deals, f, indent=4)
    print(f"✅ Scraped {len(all_deals)} unique products across multiple stores!")
else:
    print("❌ No deals found! Check the scrapers.")


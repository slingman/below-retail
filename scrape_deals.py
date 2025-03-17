import json
from scrapers.nike_scraper import scrape_nike
from scrapers.footlocker_scraper import scrape_footlocker
from scrapers.hibbett_scraper import scrape_hibbett
from scrapers.nordstrom_scraper import scrape_nordstrom
from scrapers.dicks_scraper import scrape_dicks
from scrapers.goat_scraper import scrape_goat
from scrapers.stockx_scraper import scrape_stockx

# Search term (limited to Nike Air Max 1 for now)
search_terms = ["Nike Air Max 1"]

# Dictionary to store scraped deals
deals = {}

for search_term in search_terms:
    print(f"\n🔍 Searching for {search_term} across relevant stores...")

    scrapers = {
        "Nike": scrape_nike,
        "Foot Locker": scrape_footlocker,
        "Hibbett": scrape_hibbett,
        "Nordstrom": scrape_nordstrom,
        "Dick's Sporting Goods": scrape_dicks,
        "GOAT": scrape_goat,
        "StockX": scrape_stockx
    }

    for store, scraper in scrapers.items():
        print(f"🔍 Checking {store} for {search_term}...")
        try:
            results = scraper(search_term)
            for product in results:
                style_id = product.get("style_id")
                if not style_id:
                    continue

                if style_id not in deals:
                    deals[style_id] = {
                        "name": product["name"],
                        "image": product["image"],
                        "style_id": style_id,
                        "prices": []
                    }

                deals[style_id]["prices"].append({
                    "store": store,
                    "price": product["price"],
                    "link": product["link"]
                })

        except Exception as e:
            print(f"❌ Error in {store}: {e}")

# Save scraped data to JSON
with open("deals.json", "w") as f:
    json.dump(deals, f, indent=4)

print(f"\n✅ Scraped {len(deals)} sneaker deals across multiple stores!")

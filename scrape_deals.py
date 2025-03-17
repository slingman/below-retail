import json
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.hibbett import scrape_hibbett
from scrapers.sneakers.nordstrom import scrape_nordstrom
from scrapers.sneakers.dicks import scrape_dicks
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx

# Sneaker models to search for
SNEAKER_MODELS = [
    "Nike Air Max 1",
    "Nike Air Max 90",
    "Air Jordan 1",
    "Adidas Ultraboost",
    "New Balance 550",
    "Yeezy Boost 350"
]

ALL_SCRAPERS = {
    "Nike": scrape_nike,
    "Foot Locker": scrape_footlocker,
    "Hibbett": scrape_hibbett,
    "Nordstrom": scrape_nordstrom,
    "Dick's Sporting Goods": scrape_dicks,
    "GOAT": scrape_goat,
    "StockX": scrape_stockx
}

sneaker_deals = {}

for sneaker in SNEAKER_MODELS:
    print(f"\n🔍 Searching for {sneaker} across relevant stores...")

    for store, scraper in ALL_SCRAPERS.items():
        print(f"🔍 Checking {store} for {sneaker}...")

        try:
            deals = scraper(sneaker)
            if deals:
                for deal in deals:
                    style_id = deal.get("style_id", "Unknown")
                    key = f"{deal['name']} ({style_id})"
                    
                    if key not in sneaker_deals:
                        sneaker_deals[key] = {
                            "name": deal["name"],
                            "style_id": style_id,
                            "image": deal["image"],
                            "prices": []
                        }
                    
                    sneaker_deals[key]["prices"].append({
                        "store": store,
                        "price": deal["price"],
                        "link": deal["link"],
                        "promo": deal.get("promo")
                    })
            else:
                print(f"⚠️ No results found from {store} for {sneaker}")

        except Exception as e:
            print(f"❌ Error in {scraper.__name__}: {e}")

# Save results
with open("deals.json", "w") as f:
    json.dump(sneaker_deals, f, indent=4)

print(f"\n✅ Scraped {len(sneaker_deals)} sneaker deals across multiple stores!")

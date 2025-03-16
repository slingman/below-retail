import json
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.adidas import scrape_adidas
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.hibbett import scrape_hibbett
from scrapers.sneakers.nordstrom import scrape_nordstrom
from scrapers.sneakers.dicks import scrape_dicks
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx

# **Sneaker models to search**
SNEAKER_QUERIES = [
    "Nike Air Max 1",
    "Nike Air Max 90",
    "Air Jordan 1",
    "Adidas Ultraboost",
    "New Balance 550",
    "Yeezy Boost 350"
]

# **Updated scraper dictionary**
SCRAPERS = {
    "Nike": scrape_nike,
    "Adidas": scrape_adidas,
    "Foot Locker": scrape_footlocker,
    "Hibbett": scrape_hibbett,
    "Nordstrom": scrape_nordstrom,
    "Dick's Sporting Goods": scrape_dicks,
    "GOAT": scrape_goat,
    "StockX": scrape_stockx,
}

# **Store all scraped deals**
all_deals = {}

for query in SNEAKER_QUERIES:
    print(f"\n🔍 Searching for {query} across multiple stores...")

    for store, scraper in SCRAPERS.items():
        print(f"🔍 Checking {store} for {query}...")

        try:
            results = scraper(query)  # Call scraper function with query

            if isinstance(results, dict) and results:  # Ensure valid dictionary response
                for product_name, product_data in results.items():
                    if product_name not in all_deals:
                        all_deals[product_name] = {
                            "name": product_name,
                            "image": product_data["image"],
                            "prices": []
                        }
                    all_deals[product_name]["prices"].append({
                        "store": store,
                        "price": product_data["price"],
                        "link": product_data["link"],
                        "promo": product_data.get("promo", None)
                    })
            else:
                print(f"⚠️ No results found from {store} for {query}")
        
        except Exception as e:
            print(f"❌ Error in {scraper.__name__}: {e}")

# **Save deals to JSON**
if all_deals:
    with open("deals.json", "w") as f:
        json.dump(all_deals, f, indent=4)
    print(f"✅ Scraped {len(all_deals)} sneaker deals across multiple stores!")
else:
    print("❌ No deals found! Check the scrapers.")

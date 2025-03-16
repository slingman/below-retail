from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.adidas import scrape_adidas
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.hibbett import scrape_hibbett
from scrapers.sneakers.nordstrom import scrape_nordstrom
from scrapers.sneakers.dicks import scrape_dicks
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx

# Define what stores each brand should be searched at
STORE_MAPPING = {
    "Nike": [scrape_nike, scrape_footlocker, scrape_hibbett, scrape_nordstrom, scrape_dicks, scrape_goat, scrape_stockx],
    "Adidas": [scrape_adidas, scrape_footlocker, scrape_hibbett, scrape_nordstrom, scrape_dicks, scrape_goat, scrape_stockx],
    "New Balance": [scrape_footlocker, scrape_hibbett, scrape_nordstrom, scrape_dicks, scrape_goat, scrape_stockx],
    "Yeezy": [scrape_adidas, scrape_goat, scrape_stockx],  # Yeezy is Adidas, so only search Adidas + resellers
}

# List of specific sneakers we want to search for
SNEAKER_QUERIES = [
    "Nike Air Max 1",
    "Nike Air Max 90",
    "Air Jordan 1",
    "Adidas Ultraboost",
    "New Balance 550",
    "Yeezy Boost 350",
]

# Dictionary to store results
all_deals = {}

# Loop through sneakers and only query relevant stores
for sneaker in SNEAKER_QUERIES:
    brand = None

    # Identify the brand based on the query
    if "Nike" in sneaker:
        brand = "Nike"
    elif "Adidas" in sneaker or "Yeezy" in sneaker:
        brand = "Adidas"
    elif "New Balance" in sneaker:
        brand = "New Balance"

    # Get the appropriate scrapers
    relevant_scrapers = STORE_MAPPING.get(brand, STORE_MAPPING["Nike"] + STORE_MAPPING["Adidas"] + STORE_MAPPING["New Balance"])

    print(f"\n🔍 Searching for {sneaker} across relevant stores...")
    for scraper in relevant_scrapers:
        try:
            print(f"🔍 Checking {scraper.__name__.replace('scrape_', '').title()} for {sneaker}...")
            results = scraper(sneaker)

            if results:
                all_deals[sneaker] = all_deals.get(sneaker, [])
                all_deals[sneaker].extend(results.values())
            else:
                print(f"⚠️ No results found from {scraper.__name__.replace('scrape_', '').title()} for {sneaker}")
        except Exception as e:
            print(f"❌ Error in {scraper.__name__}: {e}")

# Save the results to a JSON file
import json
with open("deals.json", "w") as f:
    json.dump(all_deals, f, indent=4)

print(f"\n✅ Scraped {len(all_deals)} sneaker deals across multiple stores!")

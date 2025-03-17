import json
from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.footlocker import scrape_footlocker
from utils.file_manager import save_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    # Scrape Nike and Foot Locker
    nike_deals = scrape_nike("air max 1")
    footlocker_deals = scrape_footlocker("air max 1")

    # Compare deals by style ID
    matched_deals = {}

    for style_id, nike_product in nike_deals.items():
        if style_id in footlocker_deals:
            footlocker_product = footlocker_deals[style_id]

            # Merge the price data
            combined_prices = nike_product["prices"] + footlocker_product["prices"]

            matched_deals[style_id] = {
                "name": nike_product["name"],
                "image": nike_product["image"],
                "prices": combined_prices,
            }

    # Save results
    save_deals(matched_deals)

    print(f"\n✅ Scraped {len(matched_deals)} deals for Nike Air Max 1!\n")


if __name__ == "__main__":
    main()

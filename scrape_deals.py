import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals
from utils.file_manager import save_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    # Fetch deals from Nike
    nike_deals = get_nike_deals()
    footlocker_deals = get_footlocker_deals()

    # Merge deals from both stores using style_id as the key
    merged_deals = {}

    for style_id, product in nike_deals.items():
        merged_deals[style_id] = product

    for style_id, product in footlocker_deals.items():
        if style_id in merged_deals:
            merged_deals[style_id]["prices"].extend(product["prices"])
        else:
            merged_deals[style_id] = product

    # Save deals to JSON
    save_deals(merged_deals)

    print(f"\n✅ Scraped {len(merged_deals)} deals for Nike Air Max 1!\n")

if __name__ == "__main__":
    main()

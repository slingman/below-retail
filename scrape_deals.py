import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

DEALS_FILE = "deals.json"

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    # Fetch deals
    nike_deals = get_nike_deals()
    footlocker_deals = get_footlocker_deals()

    combined_deals = {}

    # Merge Foot Locker deals with Nike deals based on style_id
    for style_id, nike_product in nike_deals.items():
        if style_id in footlocker_deals:
            # Combine Nike & Foot Locker prices
            nike_product["prices"].extend(footlocker_deals[style_id]["prices"])

        combined_deals[style_id] = nike_product

    # Save deals
    with open(DEALS_FILE, "w") as file:
        json.dump(combined_deals, file, indent=4)

    print(f"\n✅ Deals successfully saved to {DEALS_FILE}\n")
    print(f"✅ Scraped {len(combined_deals)} deals for Nike Air Max 1!")

if __name__ == "__main__":
    main()

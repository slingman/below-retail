import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def match_deals(nike_deals, footlocker_deals):
    """Matches Nike deals with Foot Locker deals based on style ID."""
    matched_deals = []

    for style_id, nike_deal in nike_deals.items():
        if style_id in footlocker_deals:
            footlocker_deal = footlocker_deals[style_id]
            matched_deals.append({
                "style_id": style_id,
                "nike": nike_deal,
                "footlocker": footlocker_deal
            })

    return matched_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    nike_deals = get_nike_deals()
    footlocker_deals = get_footlocker_deals()

    print(f"✅ Found {len(nike_deals)} deals at Nike.")
    print(f"✅ Found {len(footlocker_deals)} deals at Foot Locker.")

    matched_deals = match_deals(nike_deals, footlocker_deals)

    # Save to JSON
    deals_data = {
        "nike": list(nike_deals.values()),
        "footlocker": list(footlocker_deals.values()),
        "matches": matched_deals
    }

    with open("deals.json", "w") as f:
        json.dump(deals_data, f, indent=4)

    print("\n✅ Deals successfully saved to deals.json")
    print(f"\n✅ Scraped {len(nike_deals) + len(footlocker_deals)} total deals!")

if __name__ == "__main__":
    main()

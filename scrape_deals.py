import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def main():
    print("\n🔍 Searching for Nike Air Max 1 at Nike and Foot Locker...\n")

    # Scrape Nike deals
    nike_deals = get_nike_deals()
    if not nike_deals:
        print("⚠️ No deals found at Nike.")
    else:
        print(f"✅ Found {len(nike_deals)} deals at Nike.")

    # Scrape Foot Locker deals
    footlocker_deals = get_footlocker_deals()
    if not footlocker_deals:
        print("⚠️ No deals found at Foot Locker.")
    else:
        print(f"✅ Found {len(footlocker_deals)} deals at Foot Locker.")

    # Compare deals between Nike and Foot Locker
    matched_deals = []
    for nike_deal in nike_deals:
        product_name = nike_deal.get("name", "").strip()
        style_id = product_name.lower()  # Using product name as an identifier

        # Check if this product exists in Foot Locker's deals
        for footlocker_deal in footlocker_deals:
            if footlocker_deal.get("name", "").strip().lower() == style_id:
                print(f"✅ Found {product_name} at both Nike and Foot Locker!")
                matched_deals.append({
                    "product": product_name,
                    "nike_price": nike_deal["final_price"],
                    "footlocker_price": footlocker_deal["final_price"],
                    "nike_link": nike_deal["link"],
                    "footlocker_link": footlocker_deal["link"]
                })

    # Save all deals to a JSON file
    deals_data = {
        "nike": nike_deals,
        "footlocker": footlocker_deals,
        "matches": matched_deals
    }

    with open("deals.json", "w") as f:
        json.dump(deals_data, f, indent=4)

    print("\n✅ Deals successfully saved to deals.json")
    print(f"\n✅ Scraped {len(nike_deals) + len(footlocker_deals)} total deals!")

if __name__ == "__main__":
    main()

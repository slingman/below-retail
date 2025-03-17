from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

# Fetch Nike Deals
print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()
nike_style_map = {deal["style_id"]: deal for deal in nike_deals}

# Fetch Foot Locker Deals
print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Match and Compare Prices
matched_deals = []

for footlocker_deal in footlocker_deals:
    footlocker_style_id = footlocker_deal.get("style_id")
    
    if footlocker_style_id in nike_style_map:
        nike_deal = nike_style_map[footlocker_style_id]

        nike_price = nike_deal["price_final"]
        footlocker_price = footlocker_deal["price_final"]

        print(f"🔍 Style Match Found: {footlocker_style_id}")
        print(f"   - Nike: {nike_price} | {nike_deal['link']}")
        print(f"   - Foot Locker: {footlocker_price} | {footlocker_deal['link']}")

        matched_deals.append({
            "style_id": footlocker_style_id,
            "nike_price": nike_price,
            "nike_link": nike_deal["link"],
            "footlocker_price": footlocker_price,
            "footlocker_link": footlocker_deal["link"]
        })

print(f"\n✅ Total Matched Deals: {len(matched_deals)}")

from nike import get_nike_deals
from footlocker import get_footlocker_deals
import json

# Fetch Nike deals
print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

# Fetch Foot Locker deals
print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Match products by style_id (ensuring we compare the same product)
nike_style_map = {deal["style_id"]: deal for deal in nike_deals if deal.get("style_id")}
matched_deals = []

for deal in footlocker_deals:
    style_id = deal.get("style_id")
    
    if style_id and style_id in nike_style_map:
        nike_price = float(nike_style_map[style_id]["price"])
        footlocker_price = float(deal["price"])

        if nike_price < footlocker_price:
            best_deal = nike_style_map[style_id]
            best_store = "Nike"
        else:
            best_deal = deal
            best_store = "Foot Locker"

        matched_deals.append({
            "style_id": style_id,
            "product_name": best_deal["name"],
            "best_store": best_store,
            "best_price": best_deal["price"],
            "nike_price": nike_price,
            "footlocker_price": footlocker_price,
            "nike_link": nike_style_map[style_id]["link"],
            "footlocker_link": deal["url"]
        })

# Restrict to one specific product for now (for debugging)
if matched_deals:
    matched_deals = [matched_deals[0]]  # Only process the first matched deal

# Save filtered deals to a JSON file
deals_data = {
    "nike": nike_deals,
    "footlocker": footlocker_deals,
    "matches": matched_deals
}

with open("deals.json", "w") as f:
    json.dump(deals_data, f, indent=4)

print("\n✅ Done fetching sneaker deals!")

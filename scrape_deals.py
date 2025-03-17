from sneakers.nike import get_nike_deals
from sneakers.footlocker import get_footlocker_deals
import json

# Fetch deals
print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Convert deals to a dictionary for comparison
nike_style_map = {deal["style_id"]: deal for deal in nike_deals if "style_id" in deal}
footlocker_style_map = {deal["style_id"]: deal for deal in footlocker_deals if "style_id" in deal}

matches = []

for style_id, nike_deal in nike_style_map.items():
    if style_id in footlocker_style_map:
        footlocker_deal = footlocker_style_map[style_id]

        # Compare prices
        nike_price = float(nike_deal["sale_price"].replace("$", "")) if nike_deal["sale_price"] else float(nike_deal["original_price"].replace("$", ""))
        footlocker_price = float(footlocker_deal["sale_price"].replace("$", "")) if footlocker_deal["sale_price"] else float(footlocker_deal["original_price"].replace("$", ""))

        cheaper_store = "Nike" if nike_price < footlocker_price else "Foot Locker"
        cheaper_price = min(nike_price, footlocker_price)

        matches.append({
            "product_name": nike_deal["product_name"],
            "style_id": style_id,
            "cheaper_store": cheaper_store,
            "cheaper_price": cheaper_price,
            "nike_price": nike_price,
            "footlocker_price": footlocker_price,
            "nike_link": nike_deal["product_url"],
            "footlocker_link": footlocker_deal["product_url"],
        })

# Save results
data = {
    "nike": nike_deals,
    "footlocker": footlocker_deals,
    "matches": matches,
}

with open("deals.json", "w") as f:
    json.dump(data, f, indent=4)

print("\n✅ Done fetching sneaker deals!\n")

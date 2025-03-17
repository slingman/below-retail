import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

# Ensure that nike_deals is a list of dictionaries and not a raw string
if not isinstance(nike_deals, list):
    print("⚠️ Warning: Nike deals data is not in the expected format!")
    nike_deals = []  # Default to empty list if data is corrupted

# Create a style ID mapping from Nike’s scraped data
nike_style_map = {deal["style_id"]: deal for deal in nike_deals if "style_id" in deal}

print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Ensure that footlocker_deals is also a list
if not isinstance(footlocker_deals, list):
    print("⚠️ Warning: Foot Locker deals data is not in the expected format!")
    footlocker_deals = []  # Default to empty list

# Compare Nike and Foot Locker deals based on matching style IDs
matched_deals = []

for footlocker_deal in footlocker_deals:
    supplier_sku = footlocker_deal.get("supplier_sku")  # Foot Locker’s version of the style ID

    if supplier_sku and supplier_sku in nike_style_map:
        nike_deal = nike_style_map[supplier_sku]  # Get the matching Nike product
        footlocker_price = footlocker_deal["price_final"]
        nike_price = nike_deal["price_final"]

        print(f"✅ Matched {nike_deal['name']} (Nike: {nike_price}, Foot Locker: {footlocker_price})")

        matched_deals.append({
            "name": nike_deal["name"],
            "nike_price": nike_price,
            "footlocker_price": footlocker_price,
            "nike_link": nike_deal["link"],
            "footlocker_link": footlocker_deal["link"],
            "style_id": supplier_sku
        })

# Save matched deals to a JSON file
with open("matched_deals.json", "w") as f:
    json.dump(matched_deals, f, indent=4)

print(f"\n🎯 Total matched deals: {len(matched_deals)}\n")

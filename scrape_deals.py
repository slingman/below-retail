from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals
import json

# Target Style ID to match
TARGET_STYLE_ID = "FZ5808-400"

print("\nFetching Nike deal...")
nike_deal = get_nike_deals(TARGET_STYLE_ID)

print("\nFetching Foot Locker deal...")
footlocker_deal = get_footlocker_deals(TARGET_STYLE_ID)

# Compare prices if both stores have the same product
if nike_deal and footlocker_deal:
    nike_price = nike_deal["price"]
    footlocker_price = footlocker_deal["price"]

    if nike_price and footlocker_price:
        cheaper_store = "Nike" if nike_price < footlocker_price else "Foot Locker"
    else:
        cheaper_store = "Price missing for comparison"
else:
    cheaper_store = "Matching product not found on both sites"

# Save results
data = {
    "nike": nike_deal,
    "footlocker": footlocker_deal,
    "cheaper_store": cheaper_store
}

with open("deals.json", "w") as f:
    json.dump(data, f, indent=4)

print("\n✅ Done fetching and comparing sneaker deals!")

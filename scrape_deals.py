import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

# Target Style ID to compare
TARGET_STYLE_ID = "FZ5808-400"

def find_matching_product(nike_deals, footlocker_deals, target_style_id):
    """
    Compare deals from Nike and Foot Locker based on the target style ID.
    Returns the matching products and determines which store has the lower price.
    """
    nike_product = None
    footlocker_product = None

    # Search for the product with the given style ID on Nike
    for deal in nike_deals:
        if deal["style_id"] == target_style_id:
            nike_product = deal
            break

    # Search for the product with the given style ID on Foot Locker
    for deal in footlocker_deals:
        if deal["style_id"] == target_style_id:
            footlocker_product = deal
            break

    # Determine which store has the cheaper price
    if nike_product and footlocker_product:
        nike_price = float(nike_product["price"].replace("$", "")) if nike_product["price"] else None
        footlocker_price = float(footlocker_product["price"].replace("$", "")) if footlocker_product["price"] else None

        if nike_price is not None and footlocker_price is not None:
            cheaper_store = "Nike" if nike_price < footlocker_price else "Foot Locker"
        else:
            cheaper_store = "Price not available for comparison"
    else:
        cheaper_store = "Matching product not found on both sites"

    return nike_product, footlocker_product, cheaper_store

# Fetch deals from Nike and Foot Locker
print("\nFetching Nike deal...")
nike_deals = get_nike_deals()

print("\nFetching Foot Locker deal...")
footlocker_deals = get_footlocker_deals()

# Compare the specific product by style ID
nike_product, footlocker_product, cheaper_store = find_matching_product(nike_deals, footlocker_deals, TARGET_STYLE_ID)

# Save results to JSON
deals_data = {
    "nike": nike_product if nike_product else None,
    "footlocker": footlocker_product if footlocker_product else None,
    "cheaper_store": cheaper_store
}

with open("deals.json", "w") as file:
    json.dump(deals_data, file, indent=4)

print("\n✅ Done fetching and comparing sneaker deals!")

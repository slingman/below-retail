import json
from nike import get_nike_deals
from footlocker import get_footlocker_deals

def find_matching_deals(nike_deals, footlocker_deals):
    """ Compare prices for the same product using style IDs """
    matches = []

    # Create a lookup dictionary for Nike deals by style_id
    nike_style_map = {deal["style_id"]: deal for deal in nike_deals}

    for footlocker_deal in footlocker_deals:
        style_id = footlocker_deal["style_id"]

        # Ensure Foot Locker's product has a valid style_id before matching
        if style_id and style_id in nike_style_map:
            nike_deal = nike_style_map[style_id]

            # Compare prices
            nike_price = nike_deal["price"]
            footlocker_price = footlocker_deal["price"]

            cheapest_store = "Nike" if nike_price < footlocker_price else "Foot Locker"
            cheapest_price = min(nike_price, footlocker_price)

            matches.append({
                "product_name": nike_deal["name"],  
                "style_id": style_id,
                "nike_price": nike_price,
                "footlocker_price": footlocker_price,
                "cheapest_store": cheapest_store,
                "cheapest_price": cheapest_price,
                "nike_url": nike_deal["url"],
                "footlocker_url": footlocker_deal["url"]
            })

            print(f"✅ Matched: {nike_deal['name']} ({style_id})")
            print(f"   🏷 Nike Price: ${nike_price} | Foot Locker Price: ${footlocker_price}")
            print(f"   🏆 Best Buy: {cheapest_store} at ${cheapest_price}\n")

    return matches

# Step 1: Fetch deals
print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Step 2: Match by style ID and compare prices
matched_deals = find_matching_deals(nike_deals, footlocker_deals)

# Step 3: Save results
deals_data = {
    "nike": nike_deals,
    "footlocker": footlocker_deals,
    "matches": matched_deals
}

with open("deals.json", "w") as f:
    json.dump(deals_data, f, indent=4)

print("✅ Done fetching sneaker deals!\n")

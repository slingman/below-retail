import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def normalize_style_id(style_id):
    """Removes hyphen from Nike's style ID for easier matching."""
    return style_id.replace("-", "")

# Fetch deals
print("\nFetching Nike deals...\n")
nike_deals = get_nike_deals()

print("\nFetching Foot Locker deals...\n")
footlocker_deals = get_footlocker_deals()

# Normalize Nike style IDs for matching
nike_style_map = {}
for deal in nike_deals:
    if "w?q=" in deal["link"]:  # Skip search result links
        continue

    style_id = deal["link"].split("/")[-1]  # Extract style ID from Nike URL
    normalized_style_id = normalize_style_id(style_id)

    nike_style_map[normalized_style_id] = {
        "name": deal["name"],
        "price_final": deal["price_final"],
        "link": deal["link"]
    }

# Match Nike "Style" with Foot Locker "Supplier-sku #"
matched_deals = []
for deal in footlocker_deals:
    footlocker_sku = normalize_style_id(deal["supplier_sku"])  # Foot Locker’s correct SKU

    if footlocker_sku in nike_style_map:
        # Nike price details
        nike_price = nike_style_map[footlocker_sku]["price_final"]
        nike_link = nike_style_map[footlocker_sku]["link"]
        
        # Foot Locker price details
        footlocker_price = deal["price_final"]
        footlocker_link = deal["link"]
        
        # Convert prices to numbers
        try:
            nike_price_float = float(nike_price.replace("$", "").replace(",", ""))
        except ValueError:
            nike_price_float = float("inf")  # Ignore if invalid

        try:
            footlocker_price_float = float(footlocker_price.replace("$", "").replace(",", ""))
        except ValueError:
            footlocker_price_float = float("inf")  # Ignore if invalid

        # Determine the best deal
        if footlocker_price_float < nike_price_float:
            best_deal = {
                "style_id": footlocker_sku,
                "name": deal["name"],
                "best_price": footlocker_price,
                "store": "Foot Locker",
                "link": footlocker_link
            }
        else:
            best_deal = {
                "style_id": footlocker_sku,
                "name": deal["name"],
                "best_price": nike_price,
                "store": "Nike",
                "link": nike_link
            }

        matched_deals.append(best_deal)

# Output results
print("\n🔍 Matched Price Comparisons (Nike vs. Foot Locker):")
for deal in matched_deals:
    print(f"- {deal['name']} (Style ID: {deal['style_id']})")
    print(f"  ✅ Best Price: {deal['best_price']} at {deal['store']}")
    print(f"  🔗 Link: {deal['link']}\n")

# Save results to JSON file
with open("matched_deals.json", "w") as f:
    json.dump(matched_deals, f, indent=4)

print(f"✅ Total matched deals: {len(matched_deals)}")
print("📁 Matched deals saved to 'matched_deals.json'")

import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

# Target Style ID to compare (Nike's style ID)
TARGET_STYLE_ID = "FZ5808-400"

def find_matching_product(nike_deals, footlocker_deals, target_style_id):
    """
    Compares deals from Nike and Foot Locker based on the target style ID.
    For Nike, it uses the 'style_id' field.
    For Foot Locker, it compares against the 'supplier_sku' field.
    Computes the effective price (sale_price if available, else regular_price)
    and determines which store is cheaper.
    """
    nike_product = None
    footlocker_product = None

    # Normalize target for case-insensitive comparison
    target_norm = target_style_id.upper().strip()

    # Search Nike deals for matching style_id
    for deal in nike_deals:
        if isinstance(deal, dict) and deal.get("style_id", "").upper().strip() == target_norm:
            nike_product = deal
            break

    # Search Foot Locker deals for matching supplier_sku
    for deal in footlocker_deals:
        if isinstance(deal, dict) and deal.get("supplier_sku", "").upper().strip() == target_norm:
            footlocker_product = deal
            break

    # Function to compute effective price
    def effective_price(product):
        if product is None:
            return None
        return product.get("sale_price") if product.get("sale_price") is not None else product.get("regular_price")

    nike_price = effective_price(nike_product)
    fl_price = effective_price(footlocker_product)

    if nike_price is not None and fl_price is not None:
        cheaper_store = "Nike" if nike_price < fl_price else "Foot Locker"
    else:
        cheaper_store = "Price not available for comparison"

    return nike_product, footlocker_product, cheaper_store

def main():
    print("\nFetching Nike deals...")
    nike_deals = get_nike_deals()
    print(f"Fetched {len(nike_deals)} Nike deals.")

    print("\nFetching Foot Locker deals...")
    footlocker_deals = get_footlocker_deals()
    print(f"Fetched {len(footlocker_deals)} Foot Locker deals.")

    # Ensure we have lists
    if not isinstance(nike_deals, list):
        nike_deals = []
    if not isinstance(footlocker_deals, list):
        footlocker_deals = []

    nike_product, footlocker_product, cheaper_store = find_matching_product(nike_deals, footlocker_deals, TARGET_STYLE_ID)

    deals_data = {
        "nike": nike_product if nike_product else None,
        "footlocker": footlocker_product if footlocker_product else None,
        "cheaper_store": cheaper_store
    }

    with open("deals.json", "w") as file:
        json.dump(deals_data, file, indent=4)

    print("\n✅ Done fetching and comparing sneaker deals!")
    print(deals_data)

if __name__ == "__main__":
    main()

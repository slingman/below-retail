#!/usr/bin/env python3
import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def effective_price(product):
    """
    Returns the effective price: sale price if available, else regular price.
    """
    if product is None:
        return None
    return product.get("sale_price") if product.get("sale_price") is not None else product.get("regular_price")

def match_and_compare(nike_deals, footlocker_deals, target_style_id):
    """
    Matches Nike and Foot Locker products by comparing Nike's "style_id" with
    Foot Locker's "supplier_sku" (case‑insensitive). Then computes the effective price
    (sale price if available, otherwise regular price) for each and determines which
    store is cheaper.
    Returns the matched Nike product, Foot Locker product, cheaper store, and price difference.
    """
    target = target_style_id.upper().strip()
    nike_product = None
    footlocker_product = None

    # Find matching Nike product
    for prod in nike_deals:
        if prod.get("style_id", "").upper().strip() == target:
            nike_product = prod
            break

    # Find matching Foot Locker product
    for prod in footlocker_deals:
        # Foot Locker deals use "supplier_sku" as the identifier
        if prod.get("supplier_sku", "").upper().strip() == target:
            footlocker_product = prod
            break

    nike_eff = effective_price(nike_product)
    fl_eff = effective_price(footlocker_product)

    if nike_eff is not None and fl_eff is not None:
        if nike_eff < fl_eff:
            cheaper_store = "Nike"
            price_diff = fl_eff - nike_eff
        elif fl_eff < nike_eff:
            cheaper_store = "Foot Locker"
            price_diff = nike_eff - fl_eff
        else:
            cheaper_store = "Same Price"
            price_diff = 0
    else:
        cheaper_store = "Price not available for comparison"
        price_diff = None

    return nike_product, footlocker_product, cheaper_store, price_diff

def format_deal(deal, source):
    """
    Returns a formatted string for a product.
    For Nike, it uses "style_id"; for Foot Locker, it uses "supplier_sku".
    Format:
    Product Title | Identifier | Sale Price | Regular Price | Discount % | Product URL
    """
    if deal is None:
        return "No deal found."
    
    if source.lower() == "nike":
        identifier = deal.get("style_id", "N/A")
        title = deal.get("product_name", "N/A")
        url = deal.get("product_url", "N/A")
    else:
        identifier = deal.get("supplier_sku", "N/A")
        title = deal.get("product_title", "N/A")
        url = deal.get("product_url", "N/A")
        
    sale = f"${deal.get('sale_price')}" if deal.get("sale_price") is not None else "N/A"
    regular = f"${deal.get('regular_price')}" if deal.get("regular_price") is not None else "N/A"
    discount = deal.get("discount_percent", "N/A")
    
    return f"{title} | {identifier} | {sale} | {regular} | {discount} | {url}"

def main():
    print("\nFetching Nike deals...")
    nike_deals = get_nike_deals()
    print(f"Fetched {len(nike_deals)} Nike deals.")

    print("\nFetching Foot Locker deals...")
    # Ensure that your footlocker.py has been updated to scrape 4 products.
    footlocker_deals = get_footlocker_deals()
    print(f"Fetched {len(footlocker_deals)} Foot Locker deals.")

    TARGET_STYLE_ID = "FZ5808-400"  # Update as needed
    nike_prod, fl_prod, cheaper_store, price_diff = match_and_compare(nike_deals, footlocker_deals, TARGET_STYLE_ID)

    print("\n==================== Matched Product Comparison ====================")
    print(f"Target Style ID: {TARGET_STYLE_ID}")
    print("\nNike Deal:")
    print(format_deal(nike_prod, "Nike"))
    print("\nFoot Locker Deal:")
    print(format_deal(fl_prod, "Foot Locker"))
    print("\nCheaper Store:", cheaper_store)
    if price_diff is not None:
        print("Price Difference: $", price_diff)
    print("====================================================================\n")

    result = {
        "nike": nike_prod if nike_prod else None,
        "footlocker": fl_prod if fl_prod else None,
        "cheaper_store": cheaper_store,
        "price_difference": price_diff
    }
    with open("deals.json", "w") as file:
        json.dump(result, file, indent=4)

    print("✅ Done fetching and comparing sneaker deals!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def clean_supplier_sku(sku):
    if sku:
        return sku.replace("Supplier-sku #:", "").strip().upper()
    return sku

def format_deal(deal, source):
    if not deal:
        return "No deal found."
    if source.lower() == "nike":
        identifier = deal.get("style_number", "N/A")
        title = deal.get("product_name", "N/A")
        url = deal.get("product_url", "N/A")
    else:
        raw_sku = deal.get("supplier_sku", "N/A")
        identifier = clean_supplier_sku(raw_sku)
        title = deal.get("product_title", "N/A")
        url = deal.get("product_url", "N/A")
    sale = f"${deal.get('sale_price')}" if deal.get("sale_price") not in (None, "") else "N/A"
    regular = f"${deal.get('regular_price')}" if deal.get("regular_price") not in (None, "") else "N/A"
    discount = deal.get("discount_percent", "N/A")
    return f"{title} | {identifier} | {sale} | {regular} | {discount} | {url}"

def effective_price(product):
    if product is None:
        return None
    return product.get("sale_price") if product.get("sale_price") not in (None, "") else product.get("regular_price")

def match_and_compare(nike_deals, footlocker_deals, target_style_number):
    target = target_style_number.upper().strip()
    nike_product = None
    footlocker_product = None
    footlocker_skus = []
    for prod in nike_deals:
        if prod.get("style_number", "").upper().strip() == target:
            nike_product = prod
            break
    for prod in footlocker_deals:
        sku = prod.get("supplier_sku", "")
        sku_clean = clean_supplier_sku(sku)
        footlocker_skus.append(sku_clean)
        if sku_clean == target:
            footlocker_product = prod
    print("Debug: Foot Locker SKUs found:")
    for sku in footlocker_skus:
        print(" -", sku)
    nike_price = effective_price(nike_product)
    fl_price = effective_price(footlocker_product)
    if nike_price not in (None, "") and fl_price not in (None, ""):
        try:
            nike_price_val = float(nike_price)
            fl_price_val = float(fl_price)
        except ValueError:
            nike_price_val = None
            fl_price_val = None
        if nike_price_val is not None and fl_price_val is not None:
            if nike_price_val < fl_price_val:
                cheaper_store = "Nike"
                price_diff = fl_price_val - nike_price_val
            elif fl_price_val < nike_price_val:
                cheaper_store = "Foot Locker"
                price_diff = nike_price_val - fl_price_val
            else:
                cheaper_store = "Same Price"
                price_diff = 0
        else:
            cheaper_store = "Price not available for comparison"
            price_diff = None
    else:
        cheaper_store = "Price not available for comparison"
        price_diff = None
    return nike_product, footlocker_product, cheaper_store, price_diff

def main():
    print("\nFetching Nike deals...")
    nike_deals = get_nike_deals()
    print(f"Fetched {len(nike_deals)} Nike deals.")
    print("\nFetching Foot Locker deals...")
    footlocker_deals = get_footlocker_deals()
    print(f"Fetched {len(footlocker_deals)} Foot Locker deals.")
    print("\n===== Nike Deals =====")
    for deal in nike_deals:
        print(format_deal(deal, "Nike"))
    print("\n===== Foot Locker Deals =====")
    for deal in footlocker_deals:
        print(format_deal(deal, "Foot Locker"))
    TARGET_STYLE_NUMBER = "FZ5808-400"
    nike_prod, fl_prod, cheaper_store, price_diff = match_and_compare(nike_deals, footlocker_deals, TARGET_STYLE_NUMBER)
    print("\n==================== Matched Product Comparison ====================")
    print(f"Target Style Number: {TARGET_STYLE_NUMBER}\n")
    print("Nike Deal:")
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
        "price_difference": price_diff,
    }
    with open("deals.json", "w") as file:
        json.dump(result, file, indent=4)
    print("✅ Done fetching and comparing sneaker deals!")

if __name__ == "__main__":
    main()

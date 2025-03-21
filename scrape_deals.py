import json
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

# Target Style ID to compare (Nike's style ID)
TARGET_STYLE_ID = "FZ5808-400"

def find_matching_product(nike_deals, footlocker_deals, target_style_id):
    """
    Compare deals from Nike and Foot Locker based on the target style ID.
    For Nike, it uses the "style_id" field.
    For Foot Locker, it compares against the "supplier_sku" field.
    Computes the effective price (sale_price if available, else regular_price)
    and determines which store is cheaper.
    """
    nike_product = None
    footlocker_product = None

    # Normalize target for case-insensitive comparison.
    target_norm = target_style_id.upper().strip()

    # Search Nike deals for matching style_id.
    for deal in nike_deals:
        if isinstance(deal, dict) and deal.get("style_id", "").upper().strip() == target_norm:
            nike_product = deal
            break

    # Search Foot Locker deals for matching supplier_sku.
    for deal in footlocker_deals:
        if isinstance(deal, dict) and deal.get("supplier_sku", "").upper().strip() == target_norm:
            footlocker_product = deal
            break

    def effective_price(product):
        if product is None:
            return None
        return product.get("sale_price") if product.get("sale_price") is not None else product.get("regular_price")

    nike_price = effective_price(nike_product)
    fl_price = effective_price(footlocker_product)

    if nike_price is not None and fl_price is not None:
        if nike_price < fl_price:
            cheaper_store = "Nike"
            price_diff = fl_price - nike_price
        elif fl_price < nike_price:
            cheaper_store = "Foot Locker"
            price_diff = nike_price - fl_price
        else:
            cheaper_store = "Both at same price"
            price_diff = 0
    else:
        cheaper_store = "Price not available for comparison"
        price_diff = None

    return nike_product, footlocker_product, cheaper_store, price_diff

def main():
    print("\nFetching Nike deals...")
    nike_deals = get_nike_deals()
    print(f"Fetched {len(nike_deals)} Nike deals.")

    print("\nFetching Foot Locker deals...")
    footlocker_deals = get_footlocker_deals()  # Make sure footlocker.py is scraping 4 products now.
    print(f"Fetched {len(footlocker_deals)} Foot Locker deals.")

    print("\nMatching deals by Style ID / Supplier SKU...")
    nike_product, footlocker_product, cheaper_store, price_diff = find_matching_product(nike_deals, footlocker_deals, TARGET_STYLE_ID)

    # Build a readable report.
    report_lines = []
    report_lines.append("Matched Product Comparison")
    report_lines.append("==========================")
    report_lines.append(f"Target Style ID: {TARGET_STYLE_ID}")
    report_lines.append("")
    if nike_product:
        report_lines.append("Nike Deal:")
        report_lines.append(f"  Product Name: {nike_product.get('product_name')}")
        report_lines.append(f"  Style ID: {nike_product.get('style_id')}")
        report_lines.append(f"  Sale Price: ${nike_product.get('sale_price')}" if nike_product.get('sale_price') is not None else "  Sale Price: N/A")
        report_lines.append(f"  Regular Price: ${nike_product.get('regular_price')}" if nike_product.get('regular_price') is not None else "  Regular Price: N/A")
    else:
        report_lines.append("No matching Nike product found.")

    report_lines.append("")
    if footlocker_product:
        report_lines.append("Foot Locker Deal:")
        report_lines.append(f"  Product Title: {footlocker_product.get('product_title')}")
        report_lines.append(f"  Supplier SKU: {footlocker_product.get('supplier_sku')}")
        report_lines.append(f"  Sale Price: ${footlocker_product.get('sale_price')}" if footlocker_product.get('sale_price') is not None else "  Sale Price: N/A")
        report_lines.append(f"  Regular Price: ${footlocker_product.get('regular_price')}" if footlocker_product.get('regular_price') is not None else "  Regular Price: N/A")
        report_lines.append(f"  Discount: {footlocker_product.get('discount_percent')}" if footlocker_product.get('discount_percent') else "")
    else:
        report_lines.append("No matching Foot Locker product found.")

    report_lines.append("")
    report_lines.append(f"Cheaper Store: {cheaper_store}")
    if price_diff is not None:
        report_lines.append(f"Price Difference: ${price_diff:.2f}")

    report = "\n".join(report_lines)

    # Save results to JSON (optional)
    deals_data = {
        "nike": nike_product if nike_product else None,
        "footlocker": footlocker_product if footlocker_product else None,
        "cheaper_store": cheaper_store,
        "price_difference": price_diff,
        "report": report
    }
    with open("deals.json", "w") as file:
        json.dump(deals_data, file, indent=4)

    print("\n" + report)
    print("\n✅ Done fetching and comparing sneaker deals!")

if __name__ == "__main__":
    main()

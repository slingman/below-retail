#!/usr/bin/env python3
import json
from scrapers.sneakers.nike import get_nike_colorways
from scrapers.sneakers.footlocker import get_footlocker_colorways

def main():
    print("\nFetching Nike colorways...")
    nike_deals = get_nike_colorways()
    print("\nNike Colorways:")
    for deal in nike_deals:
        print(f"Style ID: {deal['style_id']} | Sale Price: {deal['sale_price']} | Regular Price: {deal['regular_price']} | URL: {deal['variant_url']}")
    
    print("\nFetching Foot Locker colorways...")
    fl_deals = get_footlocker_colorways()
    print("\nFoot Locker Colorways:")
    for deal in fl_deals:
        print(f"Product #: {deal.get('product_number', 'N/A')} | Supplier SKU: {deal.get('supplier_sku', 'N/A')} | Sale Price: {deal.get('sale_price', 'N/A')} | Regular Price: {deal.get('regular_price', 'N/A')}")
    
    result = {"nike": nike_deals, "footlocker": fl_deals}
    with open("airmax_results.json", "w") as f:
        json.dump(result, f, indent=4)
    print("\n✅ Done scraping. Results saved to airmax_results.json.")

if __name__ == "__main__":
    main()

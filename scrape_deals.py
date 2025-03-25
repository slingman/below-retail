#!/usr/bin/env python3
import time
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

def print_deal_summary(deals, store_name):
    print(f"\nSUMMARY RESULTS:")
    print(f"Total unique {store_name} products: {len(deals)}")
    
    variant_count = 0
    sale_count = 0
    for deal in deals:
        if isinstance(deal, dict):
            variant_count += 1
            if deal.get("sale_price") and deal.get("regular_price"):
                try:
                    reg = float(str(deal["regular_price"]).replace("$", "").strip())
                    sale = float(str(deal["sale_price"]).replace("$", "").strip())
                    if sale < reg:
                        sale_count += 1
                except Exception:
                    pass
    print(f"Total {store_name} variants: {variant_count}")
    print(f"{store_name} variants on sale: {sale_count}")

def main():
    print("Fetching Nike deals...")
    nike_deals = get_nike_deals()
    print("\nFetching Nike deals complete.")
    print_deal_summary(nike_deals, "Nike")

    print("\nFetching Foot Locker deals...")
    footlocker_deals = get_footlocker_deals()
    print("\nFetching Foot Locker deals complete.")
    print_deal_summary(footlocker_deals, "Foot Locker")

    all_deals = nike_deals + footlocker_deals
    print(f"\nFetched {len(all_deals)} total sneaker deals.")

if __name__ == "__main__":
    main()

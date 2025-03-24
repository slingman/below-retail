#!/usr/bin/env python3

from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

print("\nFetching Nike deals...")
nike_deals = get_nike_deals()

# Nike summary counts
unique_nike_products = len(nike_deals)
total_nike_variants = sum(len(p.get("style_variants", [])) for p in nike_deals)
total_nike_sale_variants = sum(
    1 for p in nike_deals for v in p.get("style_variants", [])
    if v.get("sale_price") and v.get("regular_price") and v.get("sale_price") < v.get("regular_price")
)

print(f"\n✅ Nike Summary:")
print(f" - Unique products found: {unique_nike_products}")
print(f" - Total style variants: {total_nike_variants}")
print(f" - Variants on sale: {total_nike_sale_variants}")

print("\nFetching Foot Locker deals...")
footlocker_deals = get_footlocker_deals()

# Optional: You can add a similar summary block for Foot Locker if desired.

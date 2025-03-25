#!/usr/bin/env python3
import time
from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

print("\nFetching Nike deals...")
nike_deals = get_nike_deals()
print("\nFetching Nike deals complete.\n")

# Nike summary
nike_unique_products = len(set(d['style_id'].split("-")[0] for d in nike_deals if 'style_id' in d))
nike_total_variants = len(nike_deals)
nike_variants_on_sale = len([
    d for d in nike_deals
    if d.get('sale_price') and d.get('price') and d.get('sale_price') < d.get('price')
])
print("\nSUMMARY RESULTS:")
print(f"Total unique Nike products: {nike_unique_products}")
print(f"Total Nike variants: {nike_total_variants}")
print(f"Nike variants on sale: {nike_variants_on_sale}")

print("\nFetching Foot Locker deals...")
footlocker_deals = get_footlocker_deals()
print("\nFetching Foot Locker deals complete.\n")

# Foot Locker summary
footlocker_unique_products = len(set(d['product_number'] for d in footlocker_deals if 'product_number' in d))
footlocker_total_variants = len(footlocker_deals)
footlocker_variants_on_sale = 0  # Sale price not handled in current footlocker.py

print("\nSUMMARY RESULTS:")
print(f"Total unique Foot Locker products: {footlocker_unique_products}")
print(f"Total Foot Locker variants: {footlocker_total_variants}")
print(f"Foot Locker variants on sale: {footlocker_variants_on_sale}")

# Combine all sneaker deals
all_deals = nike_deals + footlocker_deals
print(f"\nFetched {len(all_deals)} total sneaker deals.")

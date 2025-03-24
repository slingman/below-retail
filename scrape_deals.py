from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals
from decimal import Decimal

print("\nFetching Nike deals...")
nike_deals = get_nike_deals()

# Flatten Nike variants
flat_nike_variants = [v for product in nike_deals for v in product.get("variants", [])]

# Count logic
nike_unique_products = len(nike_deals)
nike_total_variants = len(flat_nike_variants)
nike_variants_on_sale = sum(
    1
    for v in flat_nike_variants
    if v.get("sale_price") is not None and v.get("price") is not None and Decimal(v["sale_price"]) < Decimal(v["price"])
)

print(f"\nSUMMARY RESULTS:")
print(f"Total unique Nike products: {nike_unique_products}")
print(f"Total Nike variants: {nike_total_variants}")
print(f"Nike variants on sale: {nike_variants_on_sale}")

print("\nFetching Foot Locker deals...")
footlocker_deals = get_footlocker_deals()

# Flatten Foot Locker variants
flat_footlocker_variants = [v for product in footlocker_deals for v in product.get("variants", [])]

# Count logic
footlocker_unique_products = len(footlocker_deals)
footlocker_total_variants = len(flat_footlocker_variants)
footlocker_variants_on_sale = sum(
    1
    for v in flat_footlocker_variants
    if v.get("sale_price") is not None and v.get("price") is not None and Decimal(v["sale_price"]) < Decimal(v["price"])
)

print(f"\nSUMMARY RESULTS:")
print(f"Total unique Foot Locker products: {footlocker_unique_products}")
print(f"Total Foot Locker variants: {footlocker_total_variants}")
print(f"Foot Locker variants on sale: {footlocker_variants_on_sale}")

# Combine all deals if needed
all_deals = flat_nike_variants + flat_footlocker_variants
print(f"\nFetched {len(all_deals)} total sneaker deals.")

from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

# Fetch Nike deals
print("\nFetching Nike deals...")
nike_deals = get_nike_deals()

# Print Nike summary
flat_nike_deals = [variant for product in nike_deals for variant in product.get("variants", [])]
nike_unique_products = len(nike_deals)
nike_total_variants = len(flat_nike_deals)
nike_variants_on_sale = sum(
    1 for d in flat_nike_deals if d.get("sale_price") and d.get("price") and d["sale_price"] < d["price"]
)

print("\nSUMMARY RESULTS:")
print(f"Total unique Nike products: {nike_unique_products}")
print(f"Total Nike variants: {nike_total_variants}")
print(f"Nike variants on sale: {nike_variants_on_sale}")

# Fetch Foot Locker deals
print("\nFetching Foot Locker deals...")
footlocker_deals = get_footlocker_deals()

# Print Foot Locker summary
print(f"\nFetched {len(footlocker_deals)} Foot Locker deals.")

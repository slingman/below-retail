from scrapers.sneakers.nike import get_nike_deals
from scrapers.sneakers.footlocker import get_footlocker_deals

print("\nFetching Nike deals...")
nike_deals = get_nike_deals()

nike_unique_products = len(set(d['style_id'].split("-")[0] for d in nike_deals))
nike_total_variants = len(nike_deals)
nike_on_sale = sum(1 for d in nike_deals if d.get("discount"))

print("\nNIKE SUMMARY:")
print(f"Total unique Nike products: {nike_unique_products}")
print(f"Total Nike variants: {nike_total_variants}")
print(f"Nike variants on sale: {nike_on_sale}")

print("\nFetching Foot Locker deals...")
footlocker_deals = get_footlocker_deals()

fl_unique_products = len(set(d["style_id"] for d in footlocker_deals))
fl_total_variants = len(footlocker_deals)
fl_on_sale = sum(1 for d in footlocker_deals if d.get("discount"))

print("\nFOOT LOCKER SUMMARY:")
print(f"Total unique Foot Locker products: {fl_unique_products}")
print(f"Total Foot Locker variants: {fl_total_variants}")
print(f"Foot Locker variants on sale: {fl_on_sale}")
